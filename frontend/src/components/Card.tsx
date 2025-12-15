import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface CardProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hover?: boolean;
}

export function Card({ children, className, onClick, hover = false }: CardProps) {
  const Component = onClick ? motion.button : motion.div;

  return (
    <Component
      className={clsx(
        'bg-white rounded-2xl p-4 shadow-sm border border-gray-100',
        hover && 'hover:shadow-md transition-shadow cursor-pointer',
        onClick && 'w-full text-left',
        className
      )}
      onClick={onClick}
      whileTap={onClick ? { scale: 0.98 } : undefined}
    >
      {children}
    </Component>
  );
}

interface StatCardProps {
  icon: string;
  label: string;
  value: string | number;
  subtext?: string;
}

export function StatCard({ icon, label, value, subtext }: StatCardProps) {
  return (
    <Card className="flex flex-col items-center text-center">
      <span className="text-2xl mb-1">{icon}</span>
      <span className="text-2xl font-bold text-gray-900">{value}</span>
      <span className="text-sm text-gray-500">{label}</span>
      {subtext && <span className="text-xs text-primary-500 mt-1">{subtext}</span>}
    </Card>
  );
}
