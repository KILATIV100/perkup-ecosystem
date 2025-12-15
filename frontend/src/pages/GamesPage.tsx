import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAppStore } from '../store';
import { Card, LoadingScreen } from '../components';

const gameIcons: Record<string, string> = {
  'coffee-jump': '🦘',
  'coffee-match': '🧩',
  'barista-rush': '⏱️',
  'coffee-quiz': '❓',
  'spin-wheel': '🎡',
};

export function GamesPage() {
  const { games, fetchGames, isLoadingGames } = useAppStore();

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  if (isLoadingGames) {
    return <LoadingScreen message="Завантаження ігор..." />;
  }

  return (
    <div className="p-4 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">🎮 Ігри</h1>
        <p className="text-gray-500 mt-1">
          Грай та заробляй бали лояльності
        </p>
      </div>

      {/* Games grid */}
      <div className="space-y-4">
        {games.map((game, index) => (
          <motion.div
            key={game.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Link to={`/games/${game.slug}`}>
              <Card hover className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl flex items-center justify-center text-3xl">
                  {gameIcons[game.slug] || '🎮'}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{game.name}</h3>
                  <p className="text-sm text-gray-500 line-clamp-2">
                    {game.description}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">
                      до {game.max_points_per_game} балів
                    </span>
                    {!game.is_active && (
                      <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                        Скоро
                      </span>
                    )}
                  </div>
                </div>
                <span className="text-gray-400 text-xl">→</span>
              </Card>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Info card */}
      <Card className="bg-gradient-to-r from-primary-50 to-orange-50">
        <div className="flex items-start gap-3">
          <span className="text-2xl">💡</span>
          <div>
            <h4 className="font-medium text-gray-900">Як заробляти бали?</h4>
            <p className="text-sm text-gray-600 mt-1">
              Кожна гра конвертує ігрові очки в бали лояльності. Чим вищий score — тим більше балів!
              Максимум балів за гру обмежений, тому грай частіше для більшого заробітку.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
