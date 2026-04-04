import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getMyGamification, getBadges, getDailyQuests, updateQuestProgress } from '../api/gamification';
import type { GamificationProfile, Badge, DailyQuest } from '../types';
import { Award, Star, Target, TrendingUp, CheckCircle, Clock, Trophy, Zap } from 'lucide-react';

interface BadgeProgress {
  badge: Badge;
  progress: number;
  current: number;
  target: number;
  isCompleted: boolean;
}

export default function Achievements() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<GamificationProfile | null>(null);
  const [allBadges, setAllBadges] = useState<Badge[]>([]);
  const [badgeProgress, setBadgeProgress] = useState<BadgeProgress[]>([]);
  const [dailyQuests, setDailyQuests] = useState<DailyQuest[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileData, badgesData, questsData] = await Promise.all([
        getMyGamification(),
        getBadges(),
        getDailyQuests()
      ]);
      setProfile(profileData);
      setAllBadges(badgesData);
      setDailyQuests(questsData);
      calculateProgress(profileData, badgesData);
    } catch (error) {
      console.error('Failed to load achievements:', error);
    }
  };

  const handleQuestProgress = async (questType: string) => {
    if (loading) return;
    setLoading(true);
    try {
      const updatedQuest = await updateQuestProgress(questType);
      setDailyQuests(prev => prev.map(q =>
        q.quest_type === questType ? updatedQuest : q
      ));
      // Reload profile to get updated score
      const profileData = await getMyGamification();
      setProfile(profileData);
    } catch (error) {
      console.error('Failed to update quest progress:', error);
    } finally {
      setLoading(false);
    }
  };
    // This is a simplified calculation - in real app you'd need to get actual counts from API
    const progress: BadgeProgress[] = badges.map(badge => {
      let current = 0;
      let target = 1;
      let isCompleted = profile.badges.includes(badge.id);

      // Mock progress calculation based on badge criteria
      switch (badge.id) {
        case 'first_project':
          current = profile.score > 50 ? 1 : 0;
          target = 1;
          break;
        case 'reliable':
          current = Math.min(5, Math.floor(profile.score / 20));
          target = 5;
          break;
        case 'speedster':
          current = Math.min(3, Math.floor(profile.score / 30));
          target = 3;
          break;
        case 'quality':
          current = Math.min(10, Math.floor(profile.score / 15));
          target = 10;
          break;
        case 'marathon':
          current = Math.min(50, Math.floor(profile.score / 2));
          target = 50;
          break;
        default:
          current = isCompleted ? 1 : 0;
          target = 1;
      }

      return {
        badge,
        progress: Math.min(100, (current / target) * 100),
        current,
        target,
        isCompleted
      };
    });

    setBadgeProgress(progress);
  };

  if (!profile) {
    return <div className="flex items-center justify-center h-64">Загрузка...</div>;
  }

  const completedBadges = badgeProgress.filter(bp => bp.isCompleted);
  const inProgressBadges = badgeProgress.filter(bp => !bp.isCompleted && bp.progress > 0);
  const lockedBadges = badgeProgress.filter(bp => !bp.isCompleted && bp.progress === 0);

  return (
    <div className="max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Достижения</h1>
        <p className="text-gray-600">Отслеживайте свой прогресс и получайте награды за достижения</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Star className="text-yellow-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600">Уровень</p>
              <p className="text-2xl font-bold">{profile.level}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Target className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600">Очки</p>
              <p className="text-2xl font-bold">{profile.score}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <Award className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600">Бейджей</p>
              <p className="text-2xl font-bold">{completedBadges.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <TrendingUp className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-600">До следующего уровня</p>
              <p className="text-2xl font-bold">
                {profile.next_level_at ? profile.next_level_at - profile.score : 'Макс'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Quests */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Trophy className="text-yellow-600" size={24} />
          Ежедневные задания
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dailyQuests.map(quest => (
            <div key={quest.id} className={`bg-white rounded-xl shadow-sm p-6 ${quest.is_completed ? 'border-2 border-green-200' : 'border border-gray-200'}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900">{quest.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{quest.description}</p>
                </div>
                {quest.is_completed && (
                  <CheckCircle className="text-green-600" size={24} />
                )}
              </div>

              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Прогресс</span>
                  <span>{quest.current_count}/{quest.target_count}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(100, (quest.current_count / quest.target_count) * 100)}%` }}
                  ></div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-1">
                    <Star className="text-yellow-500" size={16} />
                    <span>+{quest.reward_points} очков</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Zap className="text-purple-500" size={16} />
                    <span>+{quest.reward_xp} XP</span>
                  </div>
                </div>

                {!quest.is_completed && (
                  <button
                    onClick={() => handleQuestProgress(quest.quest_type)}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  >
                    {loading ? 'Обновление...' : 'Обновить прогресс'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Completed Badges */}
      {completedBadges.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <CheckCircle className="text-green-600" size={24} />
            Полученные бейджи ({completedBadges.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedBadges.map(({ badge }) => (
              <div key={badge.id} className="bg-white rounded-xl shadow-sm p-6 border-2 border-green-200">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-green-100 rounded-lg">
                    <Award className="text-green-600" size={32} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900">{badge.name}</h3>
                    <p className="text-sm text-gray-600">{badge.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* In Progress */}
      {inProgressBadges.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="text-blue-600" size={24} />
            В процессе ({inProgressBadges.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {inProgressBadges.map(({ badge, progress, current, target }) => (
              <div key={badge.id} className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Award className="text-blue-600" size={32} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900">{badge.name}</h3>
                    <p className="text-sm text-gray-600">{badge.desc}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Прогресс</span>
                    <span>{current}/{target}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Locked Badges */}
      {lockedBadges.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="text-gray-400" size={24} />
            Доступные бейджи ({lockedBadges.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {lockedBadges.map(({ badge }) => (
              <div key={badge.id} className="bg-gray-50 rounded-xl shadow-sm p-6 opacity-60">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gray-200 rounded-lg">
                    <Award className="text-gray-400" size={32} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-700">{badge.name}</h3>
                    <p className="text-sm text-gray-500">{badge.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}