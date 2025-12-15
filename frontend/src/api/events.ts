import apiClient from './client';
import type { Event, EventParticipant } from '../types';

interface EventsResponse {
  events: Event[];
  total: number;
}

export const eventsApi = {
  async getAll(params?: {
    status?: 'active' | 'upcoming' | 'past';
    event_type?: 'promo' | 'tournament' | 'offline' | 'challenge';
    featured?: boolean;
  }): Promise<Event[]> {
    const response = await apiClient.get<EventsResponse>('/events', { params });
    return response.data.events;
  },

  async getBySlug(slug: string): Promise<Event> {
    const response = await apiClient.get<Event>(`/events/${slug}`);
    return response.data;
  },

  async join(slug: string): Promise<{ success: boolean; participation: EventParticipant }> {
    const response = await apiClient.post(`/events/${slug}/join`);
    return response.data;
  },

  async getProgress(slug: string): Promise<{ participation: EventParticipant; event: Event }> {
    const response = await apiClient.get(`/events/${slug}/my-progress`);
    return response.data;
  },

  async claimRewards(slug: string): Promise<{ success: boolean; rewards: Record<string, unknown> }> {
    const response = await apiClient.post(`/events/${slug}/claim-rewards`);
    return response.data;
  },
};
