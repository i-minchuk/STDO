import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPortfolio } from '../api/projects';
import type { Project, PortfolioSummary } from '../types';
import StatusBadge from '../components/StatusBadge';
import SPIIndicator from '../components/SPIIndicator';
import DailyQuestWidget from '../components/DailyQuestWidget';
import { FolderOpen, AlertTriangle, CheckCircle, Clock, Calendar, ArrowUpRight, TrendingUp, Info } from 'lucide-react';
import { Card, Button, Badge } from '../components/ui';

const MOCK_SUMMARY: PortfolioSummary = { total: 5, active: 3, at_risk: 1, completed: 1 };
const MOCK_PROJECTS: Project[] = [
  { id: 1, number: 'PRJ-001', name: 'Модернизация НПЗ', status: 'active', customer: 'Газпром', start_date: '2026-01-15', end_date_plan: '2026-12-31', total_tasks: 45, completed_tasks: 28, spi: 0.92, risk_level: 'medium' },
  { id: 2, number: 'PRJ-002', name: 'Строительство ЛЭП', status: 'active', customer: 'РусГидро', start_date: '2026-02-01', end_date_plan: '2026-09-30', total_tasks: 30, completed_tasks: 25, spi: 1.05, risk_level: 'low' },
  { id: 3, number: 'PRJ-003', name: 'Реконструкция котельной', status: 'active', customer: 'ТГК-1', start_date: '2026-03-01', end_date_plan: '2026-11-15', total_tasks: 20, completed_tasks: 5, spi: 0.62, risk_level: 'high' },
];

export default function Dashboard() {
  const [summary, setSummary] = useState<PortfolioSummary>(MOCK_SUMMARY);
  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS);
  const navigate = useNavigate();

  useEffect(() => {
    getPortfolio()
      .then(d => { setSummary(d.summary); setProjects(d.projects); })
      .catch(() => {});
  }, []);

  const stats = [
    { label: 'Всего проектов', value: summary.total, icon: FolderOpen, color: 'blue', desc: 'За всё время' },
    { label: 'Активных', value: summary.active, icon: Clock, color: 'indigo', desc: 'В разработке' },
    { label: 'В зоне риска', value: summary.at_risk, icon: AlertTriangle, color: 'red', desc: 'Требуют внимания' },
    { label: 'Завершено', value: summary.completed, icon: CheckCircle, color: 'green', desc: 'Успешно закрыты' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Портфолио проектов</h1>
          <p className="text-gray-500 mt-1 flex items-center gap-2">
            <Calendar size={14} />
            Обзор состояния проектов на {new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" className="hidden sm:flex">
            <TrendingUp size={16} className="mr-2" /> Аналитика
          </Button>
          <Button size="sm" onClick={() => navigate('/documents/new')}>
            + Добавить проект
          </Button>
        </div>
      </div>

      {/* STATS GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <StatCard key={s.label} {...s} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* PROJECTS TABLE */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between px-2">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <FolderOpen size={18} className="text-primary-600" />
              Последние проекты
            </h2>
            <Button variant="ghost" size="sm" className="text-primary-600 font-semibold" onClick={() => navigate('/documents')}>
              Все проекты <ArrowUpRight size={14} className="ml-1" />
            </Button>
          </div>
          
          <Card padding="none" className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50/50 border-b border-gray-100">
                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Проект</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider hidden sm:table-cell">Заказчик</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Прогресс</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">SPI</th>
                    <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Риск</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {projects.map(p => (
                    <tr 
                      key={p.id} 
                      onClick={() => navigate(`/projects/${p.id}`)} 
                      className="group hover:bg-primary-50/30 cursor-pointer transition-all duration-200"
                    >
                      <td className="px-6 py-4">
                        <div className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">{p.name}</div>
                        <div className="text-xs text-gray-500 font-mono mt-0.5">{p.number}</div>
                      </td>
                      <td className="px-6 py-4 hidden sm:table-cell">
                        <div className="text-sm text-gray-600">{p.customer}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1.5 min-w-[100px]">
                          <div className="flex justify-between items-center text-[10px] font-bold text-gray-500 uppercase">
                            <span>Задачи</span>
                            <span>{Math.round(p.total_tasks ? (p.completed_tasks / p.total_tasks * 100) : 0)}%</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden border border-gray-200/50">
                            <div 
                              className="bg-primary-600 h-full rounded-full transition-all duration-500 ease-out shadow-sm" 
                              style={{ width: `${p.total_tasks ? (p.completed_tasks / p.total_tasks * 100) : 0}%` }} 
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <SPIIndicator value={p.spi} />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <StatusBadge status={p.risk_level} />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {projects.length === 0 && (
              <div className="py-12 text-center text-gray-400 flex flex-col items-center gap-2">
                <Info size={32} strokeWidth={1} />
                <p>Нет активных проектов</p>
              </div>
            )}
          </Card>
        </div>

        {/* SIDEBAR WIDGETS */}
        <div className="space-y-6">
          <DailyQuestWidget />
          
          <Card className="bg-primary-900 text-white overflow-hidden relative group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <TrendingUp size={80} />
            </div>
            <div className="relative z-10">
              <h3 className="font-bold text-lg mb-2">Общая эффективность</h3>
              <p className="text-primary-200 text-sm mb-4">Средний SPI по всем проектам вырос на 4.2% за прошлую неделю.</p>
              <Button variant="outline" size="sm" className="bg-white/10 border-white/20 text-white hover:bg-white/20 w-full">
                Смотреть отчет
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

/* ===== HELPER COMPONENTS ===== */

function StatCard({ label, value, icon: Icon, color, desc }: any) {
  const colors: any = {
    blue: 'bg-blue-50 text-blue-700 border-blue-100 shadow-blue-100/50',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-100 shadow-indigo-100/50',
    red: 'bg-red-50 text-red-700 border-red-100 shadow-red-100/50',
    green: 'bg-green-50 text-green-700 border-green-100 shadow-green-100/50',
  };

  return (
    <Card className={`border shadow-sm transition-all hover:shadow-md hover:-translate-y-1 ${colors[color]}`} padding="sm">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider opacity-70">{label}</p>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-black">{value}</span>
          </div>
          <p className="text-[10px] font-medium opacity-60 mt-1 italic">{desc}</p>
        </div>
        <div className={`p-2 rounded-lg bg-white/50 shadow-inner`}>
          <Icon size={24} strokeWidth={2.5} />
        </div>
      </div>
    </Card>
  );
}
