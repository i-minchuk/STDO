import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getDailyQuests } from '../api/gamification';
import type { DailyQuest } from '../types';
import { Trophy, Zap, Star, Target } from 'lucide-react';

export default function DailyQuestWidget() {
  const { user } = useAuth();
  const [quests, setQuests] = useState<DailyQuest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuests();
  }, []);

  const loadQuests = async () => {
    try {
      const questsData = await getDailyQuests();
      setQuests(questsData);
    } catch (error) {
      console.error('Failed to load daily quests:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-pulse">Загрузка...</div>;

  const completedCount = quests.filter(q => q.is_completed).length;
  const totalRewards = quests.reduce((sum, q) => sum + (q.is_completed ? q.reward_points : 0), 0);

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Trophy className="text-yellow-600" size={24} />
          <h3 className="font-bold text-gray-900">Ежедневные задания</h3>
        </div>
        <div className="text-sm text-gray-600">
          {completedCount}/{quests.length}
        </div>
      </div>

      <div className="space-y-2">
        {quests.map(quest => (
          <div key={quest.id} className="flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${quest.is_completed ? 'bg-green-500' : 'bg-gray-300'}`}></div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700 truncate">{quest.title}</span>
                <span className="text-xs text-gray-500">
                  {quest.current_count}/{quest.target_count}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all"
                  style={{ width: `${Math.min(100, (quest.current_count / quest.target_count) * 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {totalRewards > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-1 text-gray-600">
              <Star className="text-yellow-500" size={16} />
              <span>Сегодня можно заработать</span>
            </div>
            <span className="font-bold text-gray-900">+{totalRewards} очков</span>
          </div>
        </div>
      )}
    </div>
  );
}