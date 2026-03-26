import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getMyGamification, getBadges } from '../api/gamification';
import type { GamificationProfile, Badge } from '../types';
import SPIIndicator from '../components/SPIIndicator';
import { Star, Award, Target, TrendingUp } from 'lucide-react';

const MOCK_PROFILE: GamificationProfile = {
  user_id: 1, username: 'admin', full_name: 'Администратор',
  score: 320, level: 3, level_title: 'Профессионал', badges: ['reliable', 'speedster'], next_level_at: 500,
};

const MOCK_BADGES: Badge[] = [
  { id: 'reliable', name: 'Надёжный', desc: 'SPI >= 1.0 на протяжении 5 задач подряд' },
  { id: 'speedster', name: 'Скоростной', desc: '3 задачи закрыты раньше срока' },
  { id: 'quality', name: 'Качественный', desc: '0 возвратов на доработку за 10 ревизий' },
  { id: 'teamplayer', name: 'Командный', desc: 'Участие в 3+ проектах одновременно' },
  { id: 'marathon', name: 'Марафонец', desc: '50+ закрытых задач' },
];

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<GamificationProfile>(MOCK_PROFILE);
  const [badges, setBadges] = useState<Badge[]>(MOCK_BADGES);

  useEffect(() => {
    getMyGamification().then(setProfile).catch(() => {});
    getBadges().then(setBadges).catch(() => {});
  }, []);

  const xpPercent = profile.next_level_at ? (profile.score / profile.next_level_at * 100) : 100;

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Мой кабинет</h1>

      {/* Profile Card */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-3xl font-bold text-primary-700">{(user?.full_name || 'U')[0]}</span>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">{user?.full_name}</h2>
            <p className="text-gray-500">{user?.email}</p>
            <div className="flex items-center gap-4 mt-2">
              <span className="flex items-center gap-1 text-sm">
                <Star size={16} className="text-yellow-500" />
                Уровень {profile.level}: {profile.level_title}
              </span>
              <span className="flex items-center gap-1 text-sm text-gray-500">
                <Target size={16} /> {profile.score} очков
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 mb-1">SPI</div>
            <SPIIndicator value={0.95} />
          </div>
        </div>

        {/* XP Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-500 mb-1">
            <span>Прогресс до следующего уровня</span>
            <span>{profile.score} / {profile.next_level_at || '∞'}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all" style={{ width: `${Math.min(xpPercent, 100)}%` }} />
          </div>
        </div>
      </div>

      {/* Badges */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Award size={20} className="text-yellow-500" /> Бейджи
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {badges.map(b => {
            const earned = profile.badges.includes(b.id);
            return (
              <div key={b.id} className={`p-4 rounded-xl border-2 ${earned ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 bg-gray-50 opacity-50'}`}>
                <div className="flex items-center gap-2 mb-1">
                  <Award size={20} className={earned ? 'text-yellow-500' : 'text-gray-400'} />
                  <span className="font-medium">{b.name}</span>
                </div>
                <p className="text-xs text-gray-500">{b.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
