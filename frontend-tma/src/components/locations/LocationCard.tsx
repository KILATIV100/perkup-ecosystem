import { useNavigate } from 'react-router-dom';
import { Location } from '../../types';

interface LocationCardProps {
  location: Location;
}

export const LocationCard: React.FC<LocationCardProps> = ({ location }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/location/${location.id}`);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-surface rounded-2xl p-5 border border-border cursor-pointer transform transition-all duration-200 active:scale-95 hover:border-primary"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-white mb-1">
            📍 {location.name}
          </h3>
          <p className="text-sm text-gray-400">{location.address}</p>
        </div>

        {/* Check-in Icon */}
        <div className="ml-3">
          <div className="bg-green-500 text-white rounded-full w-12 h-12 flex items-center justify-center font-bold text-xl shadow-lg">
            ✓
          </div>
        </div>
      </div>

      {/* Description */}
      {location.description && (
        <p className="text-sm text-gray-500 mb-3">{location.description}</p>
      )}

      {/* Stats */}
      <div className="flex items-center justify-between pt-3 border-t border-border">
        <div className="text-xs text-gray-400">
          🏆 {location.total_checkins} чекінів
        </div>
        <div className="text-xs text-green-500">
          📏 До {location.radius_meters}м для check-in
        </div>
      </div>
    </div>
  );
};