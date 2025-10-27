export interface User {
  id: number;
  telegram_id?: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  photo_url?: string;
  points: number;
  level: number;
  total_checkins: number;
  best_game_score: number;
  created_at: string;
}

export interface Location {
  id: number;
  name: string;
  slug: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  description?: string;
  phone?: string;
  is_active: boolean;
  total_checkins: number;
  created_at: string;
}

export interface CheckinRequest {
  location_id: number;
  latitude: number;
  longitude: number;
}

export interface CheckinResponse {
  success: boolean;
  checkin: {
    id: number;
    distance_meters: number;
    points_earned: number;
    created_at: string;
  };
  user_updated: {
    total_points: number;
    total_checkins: number;
    level: number;
  };
  message: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}