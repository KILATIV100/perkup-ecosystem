import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { useLocationsStore } from '../store/locationsStore';
import { locationsService } from '../services/locations.service';
import { LocationCard } from '../components/locations/LocationCard';
import { Loading } from '../components/common/Loading';

export const Home = () => {
  const { user } = useAuthStore();
  const { locations, isLoading, setLocations, setLoading, setError } = useLocationsStore();

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    setLoading(true);
    try {
      const data = await locationsService.getAll();
      setLocations(data);
    } catch (error) {
      console.error('Failed to fetch locations:', error);
      setError('Не вдалося завантажити локації');
    }
  };

  if (isLoading) {
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 pb-20">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-purple-900/80 backdrop-blur-lg border-b border-purple-700/50 px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">☕ PerkUP</h1>
            <p className="text-purple-300 text-sm">
              Привіт, {user?.first_name || 'Гість'}!
            </p>
          </div>
          
          {/* Points Badge */}
          <div className="bg-purple-800/60 backdrop-blur-sm rounded-full px-4 py-2 border border-purple-600/40">
            <div className="text-center">
              <div className="text-xl font-bold text-white">
                {user?.points || 0}
              </div>
              <div className="text-xs text-purple-300">балів</div>
            </div>
          </div>
        </div>
      </div>

      {/* Locations List */}
      <div className="p-4 space-y-4">
        <h2 className="text-xl font-semibold text-white mb-4">
          📍 Наші локації
        </h2>

        {locations.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg mb-4">
              Локацій поки немає
            </p>
            <button
              onClick={fetchLocations}
              className="bg-primary text-white px-6 py-3 rounded-lg font-semibold"
            >
              Оновити
            </button>
          </div>
        ) : (
          locations.map((location) => (
            <LocationCard key={location.id} location={location} />
          ))
        )}
      </div>

      {/* Quick Stats */}
      <div className="px-4 mt-8">
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-purple-800/50 backdrop-blur-sm rounded-xl p-4 text-center border border-purple-700/30">
            <div className="text-2xl font-bold text-white">
              {user?.total_checkins || 0}
            </div>
            <div className="text-xs text-purple-300 mt-1">Check-ins</div>
          </div>

          <div className="bg-purple-800/50 backdrop-blur-sm rounded-xl p-4 text-center border border-purple-700/30">
            <div className="text-2xl font-bold text-white">
              {user?.level || 1}
            </div>
            <div className="text-xs text-purple-300 mt-1">Рівень</div>
          </div>

          <div className="bg-purple-800/50 backdrop-blur-sm rounded-xl p-4 text-center border border-purple-700/30">
            <div className="text-2xl font-bold text-white">
              {user?.best_game_score || 0}
            </div>
            <div className="text-xs text-purple-300 mt-1">Рекорд</div>
          </div>
        </div>
      </div>
    </div>
  );
};