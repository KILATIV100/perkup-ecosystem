import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore, useAuthStore } from '../store';
import { checkinsApi } from '../api';
import { useGeolocation, calculateDistance, useTelegram } from '../hooks';
import { Card, Button, LoadingScreen } from '../components';
import type { Location } from '../types';

export function CheckinPage() {
  const { locations, fetchLocations, isLoadingLocations } = useAppStore();
  const { user, updateUser } = useAuthStore();
  const { getCurrentPosition, isLoading: isGeoLoading, error: geoError } = useGeolocation();
  const { hapticFeedback, hapticNotification, showAlert } = useTelegram();

  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [userPosition, setUserPosition] = useState<{ lat: number; lng: number } | null>(null);
  const [isCheckinLoading, setIsCheckinLoading] = useState(false);
  const [checkinSuccess, setCheckinSuccess] = useState(false);
  const [checkinResult, setCheckinResult] = useState<{
    points: number;
    experience: number;
  } | null>(null);

  useEffect(() => {
    fetchLocations();
  }, [fetchLocations]);

  const handleGetLocation = async () => {
    try {
      const position = await getCurrentPosition();
      setUserPosition({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      });
      hapticFeedback('light');
    } catch {
      showAlert('Не вдалося отримати вашу геолокацію');
    }
  };

  const handleCheckin = async () => {
    if (!selectedLocation || !userPosition) return;

    setIsCheckinLoading(true);
    try {
      const result = await checkinsApi.create(
        selectedLocation.id,
        userPosition.lat,
        userPosition.lng
      );

      hapticNotification('success');
      setCheckinSuccess(true);
      setCheckinResult({
        points: result.user_updated.points_earned,
        experience: result.user_updated.experience_earned,
      });

      // Update user in store
      if (user) {
        updateUser({
          points: result.user_updated.points,
          experience: result.user_updated.experience,
          level: result.user_updated.level,
          total_checkins: result.user_updated.total_checkins,
        });
      }
    } catch (error: unknown) {
      hapticNotification('error');
      const message =
        error instanceof Error ? error.message : 'Не вдалося виконати check-in';
      showAlert(message);
    } finally {
      setIsCheckinLoading(false);
    }
  };

  const resetCheckin = () => {
    setCheckinSuccess(false);
    setCheckinResult(null);
    setSelectedLocation(null);
  };

  if (isLoadingLocations) {
    return <LoadingScreen message="Завантаження локацій..." />;
  }

  // Success screen
  if (checkinSuccess && checkinResult) {
    return (
      <div className="p-4 flex flex-col items-center justify-center min-h-[80vh]">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', damping: 10 }}
          className="text-8xl mb-6"
        >
          ✅
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold text-gray-900 mb-2"
        >
          Check-in успішний!
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-500 mb-6"
        >
          {selectedLocation?.name}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex gap-4 mb-8"
        >
          <div className="text-center">
            <span className="text-3xl font-bold text-primary-500">
              +{checkinResult.points}
            </span>
            <p className="text-sm text-gray-500">балів</p>
          </div>
          <div className="text-center">
            <span className="text-3xl font-bold text-green-500">
              +{checkinResult.experience}
            </span>
            <p className="text-sm text-gray-500">XP</p>
          </div>
        </motion.div>

        <Button onClick={resetCheckin}>Готово</Button>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">☕ Check-in</h1>
        <p className="text-gray-500 mt-1">
          Виберіть локацію та підтвердіть присутність
        </p>
      </div>

      {/* Location list */}
      <div className="space-y-3">
        {locations.map((location) => {
          const distance = userPosition
            ? calculateDistance(
                userPosition.lat,
                userPosition.lng,
                location.latitude,
                location.longitude
              )
            : null;

          const isNearby = distance !== null && distance <= location.checkin_radius_meters;
          const isSelected = selectedLocation?.id === location.id;

          return (
            <Card
              key={location.id}
              onClick={() => setSelectedLocation(location)}
              hover
              className={isSelected ? 'ring-2 ring-primary-500' : ''}
            >
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 bg-coffee-100 rounded-xl flex items-center justify-center text-xl">
                  ☕
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{location.name}</h3>
                  <p className="text-sm text-gray-500">{location.address}</p>
                  {distance !== null && (
                    <p
                      className={`text-sm mt-1 ${
                        isNearby ? 'text-green-500' : 'text-gray-400'
                      }`}
                    >
                      📍 {distance > 1000 ? `${(distance / 1000).toFixed(1)} км` : `${distance} м`}
                      {isNearby && ' — Ви поруч!'}
                    </p>
                  )}
                </div>
                {location.features && (
                  <div className="flex gap-1 flex-wrap">
                    {location.features.includes('wifi') && <span>📶</span>}
                    {location.features.includes('parking') && <span>🅿️</span>}
                    {location.features.includes('terrace') && <span>🌿</span>}
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Geo error */}
      <AnimatePresence>
        {geoError && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-red-50 text-red-700 p-4 rounded-xl text-sm"
          >
            {geoError}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <div className="fixed bottom-20 left-0 right-0 p-4 bg-white border-t border-gray-100">
        {!userPosition ? (
          <Button
            onClick={handleGetLocation}
            isLoading={isGeoLoading}
            className="w-full"
            size="lg"
          >
            📍 Визначити моє місцезнаходження
          </Button>
        ) : selectedLocation ? (
          <Button
            onClick={handleCheckin}
            isLoading={isCheckinLoading}
            className="w-full"
            size="lg"
          >
            ✅ Check-in в {selectedLocation.name}
          </Button>
        ) : (
          <Button disabled className="w-full" size="lg">
            Виберіть локацію
          </Button>
        )}
      </div>
    </div>
  );
}
