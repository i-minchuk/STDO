import client from './client';
import type { LeaderboardEntry, GamificationProfile, Badge } from '../types';

export const getLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  const { data } = await client.get('/api/gamification/leaderboard');
  return data;
};

export const getMyGamification = async (): Promise<GamificationProfile> => {
  const { data } = await client.get('/api/gamification/me');
  return data;
};

export const getBadges = async (): Promise<Badge[]> => {
  const { data } = await client.get('/api/gamification/badges');
  return data;
};
