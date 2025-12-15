import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { path: '/', icon: '🏠', label: 'Головна' },
  { path: '/checkin', icon: '☕', label: 'Check-in' },
  { path: '/games', icon: '🎮', label: 'Ігри' },
  { path: '/events', icon: '🎉', label: 'Івенти' },
  { path: '/profile', icon: '👤', label: 'Профіль' },
];

export function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-tg-bg flex flex-col">
      {/* Main content */}
      <main className="flex-1 pb-20 safe-area-top">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Bottom navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 safe-area-bottom">
        <div className="flex justify-around items-center h-16">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  'flex flex-col items-center justify-center w-full h-full transition-colors',
                  isActive ? 'text-primary-500' : 'text-gray-400'
                )}
              >
                <span className="text-xl mb-0.5">{item.icon}</span>
                <span className="text-xs font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute top-0 w-12 h-0.5 bg-primary-500 rounded-full"
                  />
                )}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
