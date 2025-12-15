import { useEffect, useState, useCallback } from 'react';
import WebApp from '@twa-dev/sdk';

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  photo_url?: string;
}

export function useTelegram() {
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [initData, setInitData] = useState<string>('');

  useEffect(() => {
    // Initialize Telegram WebApp
    if (WebApp.initDataUnsafe?.user) {
      setUser(WebApp.initDataUnsafe.user);
      setInitData(WebApp.initData);
    }

    // Signal that the app is ready
    WebApp.ready();
    setIsReady(true);

    // Expand to full height
    WebApp.expand();

    // Set header color
    WebApp.setHeaderColor('#f17322');
    WebApp.setBackgroundColor('#ffffff');
  }, []);

  const showAlert = useCallback((message: string) => {
    WebApp.showAlert(message);
  }, []);

  const showConfirm = useCallback((message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      WebApp.showConfirm(message, resolve);
    });
  }, []);

  const showPopup = useCallback((params: {
    title?: string;
    message: string;
    buttons?: Array<{ id: string; type?: 'ok' | 'close' | 'cancel' | 'default' | 'destructive'; text: string }>;
  }): Promise<string> => {
    return new Promise((resolve) => {
      WebApp.showPopup(params, resolve);
    });
  }, []);

  const hapticFeedback = useCallback((type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => {
    WebApp.HapticFeedback.impactOccurred(type);
  }, []);

  const hapticNotification = useCallback((type: 'error' | 'success' | 'warning') => {
    WebApp.HapticFeedback.notificationOccurred(type);
  }, []);

  const close = useCallback(() => {
    WebApp.close();
  }, []);

  const setMainButton = useCallback((text: string, onClick: () => void, isVisible = true) => {
    WebApp.MainButton.setText(text);
    WebApp.MainButton.onClick(onClick);
    if (isVisible) {
      WebApp.MainButton.show();
    } else {
      WebApp.MainButton.hide();
    }
  }, []);

  const hideMainButton = useCallback(() => {
    WebApp.MainButton.hide();
  }, []);

  const setBackButton = useCallback((onClick: () => void) => {
    WebApp.BackButton.onClick(onClick);
    WebApp.BackButton.show();
  }, []);

  const hideBackButton = useCallback(() => {
    WebApp.BackButton.hide();
  }, []);

  return {
    user,
    isReady,
    initData,
    colorScheme: WebApp.colorScheme,
    themeParams: WebApp.themeParams,
    platform: WebApp.platform,
    version: WebApp.version,
    showAlert,
    showConfirm,
    showPopup,
    hapticFeedback,
    hapticNotification,
    close,
    setMainButton,
    hideMainButton,
    setBackButton,
    hideBackButton,
  };
}
