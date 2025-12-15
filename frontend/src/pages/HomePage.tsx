import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore, useAppStore } from '../store';
import { Card, StatCard, Avatar, ProgressBar, LoadingScreen } from '../components';

export function HomePage() {
  const { user, isLoading: isAuthLoading } = useAuthStore();
  const { events, fetchEvents, isLoadingEvents } = useAppStore();

  useEffect(() => {
    fetchEvents('active');
  }, [fetchEvents]);

  if (isAuthLoading || !user) {
    return <LoadingScreen message="Завантаження профілю..." />;
  }

  const levelNames: Record<number, string> = {
    1: 'Новачок',
    2: 'Кавоман',
    3: 'Бариста-учень',
    4: 'Бариста',
    5: 'Старший бариста',
    6: 'Майстер',
    7: 'Експерт',
    8: 'Гуру кави',
    9: 'Легенда',
    10: 'Coffee King',
  };

  const levelThresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500];
  const currentLevelXP = levelThresholds[user.level - 1] || 0;
  const nextLevelXP = levelThresholds[user.level] || levelThresholds[9];
  const progressXP = user.experience - currentLevelXP;
  const neededXP = nextLevelXP - currentLevelXP;

  return (
    <div className="p-4 space-y-6">
      {/* Welcome header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <Avatar src={user.photo_url} name={user.first_name} size="lg" />
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Привіт, {user.first_name || user.username}! 👋
          </h1>
          <p className="text-gray-500">
            Level {user.level} — {levelNames[user.level]}
          </p>
        </div>
      </motion.div>

      {/* Level progress */}
      <Card>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Рівень {user.level}
          </span>
          <span className="text-xs text-gray-500">
            {progressXP} / {neededXP} XP
          </span>
        </div>
        <ProgressBar value={progressXP} max={neededXP} showValue={false} />
        <p className="text-xs text-gray-500 mt-2">
          До наступного рівня: {neededXP - progressXP} XP
        </p>
      </Card>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        <StatCard icon="💰" label="Бали" value={user.points} />
        <StatCard icon="☕" label="Check-ins" value={user.total_checkins} />
        <StatCard icon="🎮" label="Ігор зіграно" value={user.total_games_played} />
        <StatCard icon="🏆" label="Рекорд" value={user.best_game_score} />
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-3">
        <Link to="/checkin">
          <Card hover className="text-center py-6">
            <span className="text-3xl mb-2 block">☕</span>
            <span className="font-medium text-gray-900">Check-in</span>
            <span className="text-xs text-gray-500 block">+1 бал</span>
          </Card>
        </Link>
        <Link to="/games">
          <Card hover className="text-center py-6">
            <span className="text-3xl mb-2 block">🎮</span>
            <span className="font-medium text-gray-900">Ігри</span>
            <span className="text-xs text-gray-500 block">до 25 балів</span>
          </Card>
        </Link>
      </div>

      {/* Active events */}
      {!isLoadingEvents && events.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            🎉 Активні івенти
          </h2>
          <div className="space-y-3">
            {events.slice(0, 3).map((event) => (
              <Link key={event.id} to={`/events/${event.slug}`}>
                <Card hover>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-xl">
                      {event.event_type === 'promo' && '🎁'}
                      {event.event_type === 'tournament' && '🏆'}
                      {event.event_type === 'offline' && '📍'}
                      {event.event_type === 'challenge' && '⭐'}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{event.title}</h3>
                      <p className="text-sm text-gray-500">
                        {event.short_description || event.description?.slice(0, 50)}
                      </p>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
