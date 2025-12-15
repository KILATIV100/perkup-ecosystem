import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAppStore } from '../store';
import { Card, Button, LoadingScreen } from '../components';

const eventTypeLabels: Record<string, string> = {
  promo: '🎁 Промо',
  tournament: '🏆 Турнір',
  offline: '📍 Офлайн',
  challenge: '⭐ Челендж',
};

type FilterType = 'active' | 'upcoming' | 'past';

export function EventsPage() {
  const { events, fetchEvents, isLoadingEvents } = useAppStore();
  const [filter, setFilter] = useState<FilterType>('active');

  useEffect(() => {
    fetchEvents(filter);
  }, [fetchEvents, filter]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('uk-UA', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="p-4 space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900">🎉 Івенти</h1>
        <p className="text-gray-500 mt-1">
          Бери участь та вигравай призи
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 bg-gray-100 p-1 rounded-xl">
        {(['active', 'upcoming', 'past'] as FilterType[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
              filter === f
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {f === 'active' && 'Активні'}
            {f === 'upcoming' && 'Скоро'}
            {f === 'past' && 'Минулі'}
          </button>
        ))}
      </div>

      {isLoadingEvents ? (
        <LoadingScreen message="Завантаження івентів..." />
      ) : events.length === 0 ? (
        <div className="text-center py-12">
          <span className="text-5xl mb-4 block">🎈</span>
          <h3 className="text-lg font-medium text-gray-900">
            Немає івентів
          </h3>
          <p className="text-gray-500 mt-1">
            {filter === 'active' && 'Зараз немає активних івентів'}
            {filter === 'upcoming' && 'Немає запланованих івентів'}
            {filter === 'past' && 'Історія івентів порожня'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {events.map((event, index) => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Link to={`/events/${event.slug}`}>
                <Card hover>
                  {event.cover_image && (
                    <img
                      src={event.cover_image}
                      alt={event.title}
                      className="w-full h-32 object-cover rounded-xl mb-3"
                    />
                  )}
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">
                          {eventTypeLabels[event.event_type]}
                        </span>
                        {event.is_featured && (
                          <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                            ⭐ Featured
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-900">
                        {event.title}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {event.short_description || event.description}
                      </p>
                      <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                        <span>📅 {formatDate(event.starts_at)}</span>
                        {event.max_participants && (
                          <span>
                            👥 {event.current_participants}/{event.max_participants}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="text-gray-400 text-xl">→</span>
                  </div>
                </Card>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
