import { useEffect, useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { useTelegram } from './hooks';
import { useAuthStore } from './store';
import { Layout, LoadingScreen } from './components';
import {
  HomePage,
  CheckinPage,
  GamesPage,
  EventsPage,
  LeaderboardPage,
  ProfilePage,
} from './pages';

function App() {
  const { isReady, initData, hideBackButton, setBackButton } = useTelegram();
  const { authenticate, isAuthenticated, isLoading, error } = useAuthStore();
  const [isInitializing, setIsInitializing] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  // Authentication effect
  useEffect(() => {
    const init = async () => {
      if (!isReady) return;

      // If already authenticated, skip
      if (isAuthenticated) {
        setIsInitializing(false);
        return;
      }

      // If we have initData, try to authenticate
      if (initData) {
        try {
          await authenticate(initData);
        } catch (err) {
          console.error('Authentication failed:', err);
        }
      }

      setIsInitializing(false);
    };

    init();
  }, [isReady, initData, authenticate, isAuthenticated]);

  // Back button handling
  useEffect(() => {
    if (location.pathname !== '/') {
      setBackButton(() => navigate(-1));
    } else {
      hideBackButton();
    }
  }, [location.pathname, navigate, setBackButton, hideBackButton]);

  // Loading state
  if (!isReady || isInitializing || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-primary-50 to-white">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-bounce">☕</div>
          <LoadingScreen message="Завантаження PerkUP..." />
        </div>
      </div>
    );
  }

  // Auth error state
  if (error && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-6xl mb-4">😕</div>
          <h1 className="text-xl font-bold text-gray-900 mb-2">
            Помилка авторизації
          </h1>
          <p className="text-gray-500 mb-4">{error}</p>
          <p className="text-sm text-gray-400">
            Будь ласка, спробуйте перезапустити додаток
          </p>
        </div>
      </div>
    );
  }

  // Not authenticated (fallback for development without Telegram)
  if (!isAuthenticated && !initData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-primary-50 to-white">
        <div className="text-center max-w-sm">
          <div className="text-6xl mb-4">☕</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            PerkUP
          </h1>
          <p className="text-gray-500 mb-6">
            Відкрийте цей додаток через Telegram Mini App
          </p>
          <a
            href="https://t.me/perkup_ua_bot"
            className="inline-block bg-primary-500 text-white px-6 py-3 rounded-xl font-medium"
          >
            Відкрити в Telegram
          </a>
        </div>
      </div>
    );
  }

  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<HomePage />} />
          <Route path="/checkin" element={<CheckinPage />} />
          <Route path="/games" element={<GamesPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </AnimatePresence>
    </Layout>
  );
}

export default App;
