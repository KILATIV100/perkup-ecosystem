import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { leaderboardApi } from '../api';
import { useAuthStore } from '../store';
import { Card, Avatar, LoadingScreen } from '../components';
import type { Leaderboard, LeaderboardEntry } from '../types';

type PeriodType = 'daily' | 'weekly' | 'monthly' | 'all_time';

export function LeaderboardPage() {
  const { user } = useAuthStore();
  const [leaderboard, setLeaderboard] = useState<Leaderboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [period, setPeriod] = useState<PeriodType>('weekly');

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setIsLoading(true);
      try {
        const data = await leaderboardApi.get({ period });
        setLeaderboard(data);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, [period]);

  const getMedalEmoji = (rank: number) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return null;
  };

  const renderEntry = (entry: LeaderboardEntry, highlight = false) => {
    const medal = getMedalEmoji(entry.rank);

    return (
      <motion.div
        key={entry.user_id}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: entry.rank * 0.05 }}
      >
        <Card
          className={`flex items-center gap-3 ${
            highlight ? 'ring-2 ring-primary-500 bg-primary-50' : ''
          }`}
        >
          <div className="w-8 text-center">
            {medal ? (
              <span className="text-xl">{medal}</span>
            ) : (
              <span className="text-sm font-medium text-gray-500">
                #{entry.rank}
              </span>
            )}
          </div>
          <Avatar
            src={entry.photo_url}
            name={entry.first_name || entry.username}
            size="sm"
          />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 truncate">
              {entry.first_name || entry.username || `User ${entry.user_id}`}
            </p>
            <p className="text-xs text-gray-500">
              {entry.games_played} ігор
            </p>
          </div>
          <div className="text-right">
            <p className="font-bold text-gray-900">{entry.total_score}</p>
            <p className="text-xs text-gray-500">очків</p>
          </div>
        </Card>
      </motion.div>
    );
  };

  return (
    <div className="p-4 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">🏆 Leaderboard</h1>
        <p className="text-gray-500 mt-1">
          Топ гравців тижня
        </p>
      </div>

      {/* Period filter */}
      <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
        {(['daily', 'weekly', 'monthly', 'all_time'] as PeriodType[]).map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              period === p
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {p === 'daily' && '📅 Сьогодні'}
            {p === 'weekly' && '📆 Тиждень'}
            {p === 'monthly' && '🗓️ Місяць'}
            {p === 'all_time' && '♾️ За весь час'}
          </button>
        ))}
      </div>

      {isLoading ? (
        <LoadingScreen message="Завантаження рейтингу..." />
      ) : !leaderboard || leaderboard.entries.length === 0 ? (
        <div className="text-center py-12">
          <span className="text-5xl mb-4 block">🎮</span>
          <h3 className="text-lg font-medium text-gray-900">
            Ще немає даних
          </h3>
          <p className="text-gray-500 mt-1">
            Будь першим у таблиці лідерів!
          </p>
        </div>
      ) : (
        <>
          {/* Top 3 podium */}
          {leaderboard.entries.length >= 3 && (
            <div className="flex items-end justify-center gap-2 py-4">
              {/* 2nd place */}
              <div className="text-center">
                <Avatar
                  src={leaderboard.entries[1]?.photo_url}
                  name={leaderboard.entries[1]?.first_name}
                  size="lg"
                  className="mx-auto mb-2"
                />
                <span className="text-2xl">🥈</span>
                <p className="text-sm font-medium truncate max-w-[80px]">
                  {leaderboard.entries[1]?.first_name || 'User'}
                </p>
                <p className="text-xs text-gray-500">
                  {leaderboard.entries[1]?.total_score}
                </p>
              </div>

              {/* 1st place */}
              <div className="text-center -mt-4">
                <Avatar
                  src={leaderboard.entries[0]?.photo_url}
                  name={leaderboard.entries[0]?.first_name}
                  size="xl"
                  className="mx-auto mb-2 ring-4 ring-yellow-400"
                />
                <span className="text-3xl">🥇</span>
                <p className="text-sm font-bold truncate max-w-[80px]">
                  {leaderboard.entries[0]?.first_name || 'User'}
                </p>
                <p className="text-xs text-gray-500">
                  {leaderboard.entries[0]?.total_score}
                </p>
              </div>

              {/* 3rd place */}
              <div className="text-center">
                <Avatar
                  src={leaderboard.entries[2]?.photo_url}
                  name={leaderboard.entries[2]?.first_name}
                  size="lg"
                  className="mx-auto mb-2"
                />
                <span className="text-2xl">🥉</span>
                <p className="text-sm font-medium truncate max-w-[80px]">
                  {leaderboard.entries[2]?.first_name || 'User'}
                </p>
                <p className="text-xs text-gray-500">
                  {leaderboard.entries[2]?.total_score}
                </p>
              </div>
            </div>
          )}

          {/* My position */}
          {leaderboard.my_entry && leaderboard.my_position && (
            <div className="border-t border-b border-gray-100 py-4">
              <p className="text-sm text-gray-500 mb-2">Твоя позиція</p>
              {renderEntry(leaderboard.my_entry, true)}
            </div>
          )}

          {/* Full list */}
          <div className="space-y-2">
            {leaderboard.entries.slice(3).map((entry) =>
              renderEntry(entry, user?.id === entry.user_id)
            )}
          </div>
        </>
      )}
    </div>
  );
}
