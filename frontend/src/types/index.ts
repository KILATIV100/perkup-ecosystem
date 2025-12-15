// User types
export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  photo_url: string | null;
  points: number;
  experience: number;
  level: number;
  total_checkins: number;
  total_games_played: number;
  best_game_score: number;
  referral_code: string | null;
  created_at: string;
}

export interface UserProfile extends User {
  level_name: string;
  level_bonus: number;
  next_level_xp: number;
  xp_to_next_level: number;
  notifications_enabled: boolean;
  language_code: string;
}

// Location types
export interface Location {
  id: number;
  name: string;
  slug: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  checkin_radius_meters: number;
  description: string | null;
  working_hours: Record<string, string> | null;
  features: string[] | null;
  cover_image: string | null;
  photos: string[] | null;
  total_checkins: number;
  is_active: boolean;
  created_at: string;
}

// Checkin types
export interface Checkin {
  id: number;
  location_id: number;
  location_name: string;
  user_latitude: number | null;
  user_longitude: number | null;
  distance_meters: number | null;
  points_earned: number;
  experience_earned: number;
  checkin_date: string;
  created_at: string;
}

export interface CheckinResult {
  success: boolean;
  checkin: Checkin;
  user_updated: {
    points: number;
    experience: number;
    level: number;
    total_checkins: number;
    points_earned: number;
    experience_earned: number;
  };
}

// Game types
export interface Game {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  max_points_per_game: number;
  icon_url: string | null;
  cover_image: string | null;
  is_active: boolean;
}

export interface GameSession {
  id: string;
  game_id: number;
  game_name: string;
  score: number;
  duration_seconds: number | null;
  points_earned: number;
  experience_earned: number;
  is_completed: boolean;
  created_at: string;
  completed_at: string | null;
}

// Event types
export interface Event {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  short_description: string | null;
  event_type: 'promo' | 'tournament' | 'offline' | 'challenge';
  starts_at: string;
  ends_at: string;
  requirements: Record<string, unknown>;
  rewards: Record<string, unknown>;
  max_participants: number | null;
  current_participants: number;
  location_id: number | null;
  cover_image: string | null;
  status: string;
  is_featured: boolean;
  is_active: boolean;
  is_upcoming: boolean;
  is_past: boolean;
  created_at: string;
}

export interface EventParticipant {
  id: string;
  event_id: string;
  user_id: number;
  progress: Record<string, unknown>;
  progress_percentage: number;
  status: string;
  rewards_claimed: boolean;
  registered_at: string;
  completed_at: string | null;
}

// Leaderboard types
export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string | null;
  first_name: string | null;
  photo_url: string | null;
  total_score: number;
  best_score: number;
  games_played: number;
}

export interface Leaderboard {
  period_type: 'daily' | 'weekly' | 'monthly' | 'all_time';
  period_date: string;
  game_id: number | null;
  game_name: string | null;
  entries: LeaderboardEntry[];
  total_entries: number;
  my_position: number | null;
  my_entry: LeaderboardEntry | null;
}

// API response types
export interface ApiError {
  detail: string | { error_code: string; message: string; details?: Record<string, unknown> };
}
