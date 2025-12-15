import { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuthStore } from '../store';
import { usersApi } from '../api';
import { useTelegram } from '../hooks';
import { Card, Avatar, ProgressBar, Button, LoadingScreen } from '../components';

export function ProfilePage() {
  const { user, updateUser, isLoading } = useAuthStore();
  const { showAlert, showConfirm } = useTelegram();
  const [isSaving, setIsSaving] = useState(false);

  if (isLoading || !user) {
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

  const levelBonus = Math.round((user.level_bonus || 0) * 100);

  const handleToggleNotifications = async () => {
    const newValue = !user.notifications_enabled;
    const confirmed = await showConfirm(
      newValue
        ? 'Увімкнути сповіщення?'
        : 'Вимкнути сповіщення?'
    );

    if (!confirmed) return;

    setIsSaving(true);
    try {
      await usersApi.updateSettings({ notifications_enabled: newValue });
      updateUser({ notifications_enabled: newValue });
      showAlert(newValue ? 'Сповіщення увімкнено' : 'Сповіщення вимкнено');
    } catch {
      showAlert('Не вдалося змінити налаштування');
    } finally {
      setIsSaving(false);
    }
  };

  const copyReferralLink = () => {
    if (user.referral_code) {
      const link = `https://t.me/perkup_ua_bot?start=ref_${user.referral_code}`;
      navigator.clipboard.writeText(link);
      showAlert('Посилання скопійовано!');
    }
  };

  return (
    <div className="p-4 space-y-6">
      {/* Profile header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <Avatar
          src={user.photo_url}
          name={user.first_name}
          size="xl"
          className="mx-auto mb-4"
        />
        <h1 className="text-2xl font-bold text-gray-900">
          {user.first_name} {user.last_name}
        </h1>
        {user.username && (
          <p className="text-gray-500">@{user.username}</p>
        )}
      </motion.div>

      {/* Level card */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <div>
            <span className="text-2xl font-bold text-gray-900">
              Level {user.level}
            </span>
            <span className="ml-2 text-primary-500 font-medium">
              {levelNames[user.level]}
            </span>
          </div>
          {levelBonus > 0 && (
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
              +{levelBonus}% бонус
            </span>
          )}
        </div>
        <ProgressBar value={progressXP} max={neededXP} showValue={false} />
        <p className="text-xs text-gray-500 mt-2">
          {user.experience} XP · До Level {user.level + 1}: {neededXP - progressXP} XP
        </p>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="text-center">
          <span className="text-3xl">💰</span>
          <p className="text-2xl font-bold text-gray-900 mt-1">{user.points}</p>
          <p className="text-sm text-gray-500">балів</p>
        </Card>
        <Card className="text-center">
          <span className="text-3xl">☕</span>
          <p className="text-2xl font-bold text-gray-900 mt-1">{user.total_checkins}</p>
          <p className="text-sm text-gray-500">check-ins</p>
        </Card>
        <Card className="text-center">
          <span className="text-3xl">🎮</span>
          <p className="text-2xl font-bold text-gray-900 mt-1">{user.total_games_played}</p>
          <p className="text-sm text-gray-500">ігор</p>
        </Card>
        <Card className="text-center">
          <span className="text-3xl">🏆</span>
          <p className="text-2xl font-bold text-gray-900 mt-1">{user.best_game_score}</p>
          <p className="text-sm text-gray-500">рекорд</p>
        </Card>
      </div>

      {/* Referral */}
      <Card>
        <h3 className="font-semibold text-gray-900 mb-2">👥 Запроси друзів</h3>
        <p className="text-sm text-gray-500 mb-3">
          Отримуй 10 балів за кожного друга, який приєднається за твоїм посиланням
        </p>
        <Button onClick={copyReferralLink} variant="secondary" className="w-full">
          📋 Скопіювати посилання
        </Button>
      </Card>

      {/* Settings */}
      <Card>
        <h3 className="font-semibold text-gray-900 mb-4">⚙️ Налаштування</h3>

        <div className="space-y-4">
          {/* Notifications toggle */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Сповіщення</p>
              <p className="text-sm text-gray-500">
                Отримувати push-сповіщення
              </p>
            </div>
            <button
              onClick={handleToggleNotifications}
              disabled={isSaving}
              className={`relative w-12 h-7 rounded-full transition-colors ${
                user.notifications_enabled ? 'bg-primary-500' : 'bg-gray-300'
              }`}
            >
              <motion.div
                className="absolute top-1 w-5 h-5 bg-white rounded-full shadow"
                animate={{ left: user.notifications_enabled ? '1.5rem' : '0.25rem' }}
              />
            </button>
          </div>

          {/* Language */}
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Мова</p>
              <p className="text-sm text-gray-500">
                Мова інтерфейсу
              </p>
            </div>
            <span className="text-gray-600">🇺🇦 Українська</span>
          </div>
        </div>
      </Card>

      {/* App info */}
      <div className="text-center text-xs text-gray-400 pb-4">
        <p>PerkUP v1.0.0</p>
        <p>© 2025 PerkUP Coffee</p>
      </div>
    </div>
  );
}
