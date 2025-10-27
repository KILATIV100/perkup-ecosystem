import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useTelegram } from './hooks/useTelegram';
import { useAuthStore } from './store/authStore';
import { authService } from './services/auth.service';
import { Home } from './pages/Home';
import { Loading } from './components/common/Loading';

function App() {
  const { initData, isReady } = useTelegram();
  const { setUser, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Перевіряємо чи є збережений користувач
    const savedUser = authService.getUser();
    if (savedUser) {
      setUser(savedUser);
    }
  }, []);

  useEffect(() => {
    // Автоматична авторизація через Telegram
    if (isReady && initData && !isAuthenticated) {
      handleAuth();
    }
  }, [isReady, initData, isAuthenticated]);

  const handleAuth = async () => {
    try {
      const response = await authService.loginWithTelegram(initData);
      setUser(response.user);
    } catch (error) {
      console.error('Auth failed:', error);
    }
  };

  if (!isReady) {
    return <Loading />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;