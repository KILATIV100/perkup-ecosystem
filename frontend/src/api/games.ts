import apiClient from './client';
import type { Game, GameSession } from '../types';

interface GamesResponse {
  games: Game[];
}

interface SessionStartResponse {
  session_id: string;
  game: Game;
}

interface SessionEndResponse {
  session: GameSession;
  points_earned: number;
  leaderboard_position: Record<string, number>;
}

export const gamesApi = {
  async getAll(): Promise<Game[]> {
    const response = await apiClient.get<GamesResponse>('/games');
    return response.data.games;
  },

  async getBySlug(slug: string): Promise<Game> {
    const response = await apiClient.get<Game>(`/games/${slug}`);
    return response.data;
  },

  async startSession(gameSlug: string, platform: string = 'tma'): Promise<SessionStartResponse> {
    const response = await apiClient.post<SessionStartResponse>(`/games/${gameSlug}/sessions`, {
      platform,
    });
    return response.data;
  },

  async endSession(sessionId: string, score: number, durationSeconds: number): Promise<SessionEndResponse> {
    const response = await apiClient.post<SessionEndResponse>(`/games/sessions/${sessionId}/end`, {
      score,
      duration_seconds: durationSeconds,
    });
    return response.data;
  },
};
