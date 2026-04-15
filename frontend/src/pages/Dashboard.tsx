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
    { label: 'Всего проектов', value: summary.total, icon: FolderOpen, color: 'docs', desc: 'За всё время' },
    { label: 'Активных', value: summary.active, icon: Clock, color: 'engineering', desc: 'В разработке' },
    { label: 'В зоне риска', value: summary.at_risk, icon: AlertTriangle, color: 'audit', desc: 'Требуют внимания' },
    { label: 'Завершено', value: summary.completed, icon: CheckCircle, color: 'success', desc: 'Успешно закрыты' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight page-title">Портфолио проектов</h1>
          <p className="text-secondary-token mt-1 flex items-center gap-2">
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
          <h2 className="text-lg font-semibold flex items-center gap-2 section-title">
            <FolderOpen size={18} className="text-primary" />
            Последние проекты
          </h2>
          <Button variant="ghost" size="sm" className="font-semibold" style={{ color: 'var(--primary)' }} onClick={() => navigate('/documents')}>
            Все проекты <ArrowUpRight size={14} className="ml-1" />
          </Button>
        </div>

          <Card padding="none" className="overflow-hidden surface-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b" style={{ backgroundColor: 'var(--bg-surface-2)', borderColor: 'var(--border-default)' }}>
                    <th className="px-6 py-4 text-xs font-bold text-tertiary-token uppercase tracking-wider">Проект</th>
                    <th className="px-6 py-4 text-xs font-bold text-tertiary-token uppercase tracking-wider hidden sm:table-cell">Заказчик</th>
                    <th className="px-6 py-4 text-xs font-bold text-tertiary-token uppercase tracking-wider">Прогресс</th>
                    <th className="px-6 py-4 text-xs font-bold text-tertiary-token uppercase tracking-wider">SPI</th>
                    <th className="px-6 py-4 text-xs font-bold text-tertiary-token uppercase tracking-wider">Риск</th>
                  </tr>
                </thead>
                <tbody className="divide-y" style={{ divideColor: 'var(--border-light)' }}>
                  {projects.map(p => (
                    <tr 
                      key={p.id} 
                      onClick={() => navigate(`/projects/${p.id}`)} 
                      className="group cursor-pointer transition-all duration-200"
                      style={{ '--tw-bg-opacity': '1', backgroundColor: 'transparent' } as any}
                    >
                      <td className="px-6 py-4">
                        <div className="font-semibold group-hover:text-primary transition-colors" style={{ color: 'var(--text-primary)' }}>{p.name}</div>
                        <div className="text-xs font-mono mt-0.5" style={{ color: 'var(--text-tertiary)' }}>{p.number}</div>
                      </td>
                      <td className="px-6 py-4 hidden sm:table-cell">
                        <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>{p.customer}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1.5 min-w-[100px]">
                          <div className="flex justify-between items-center text-[10px] font-bold text-tertiary-token uppercase">
                            <span>Задачи</span>
                            <span>{Math.round(p.total_tasks ? (p.completed_tasks / p.total_tasks * 100) : 0)}%</span>
                          </div>
                          <div className="w-full rounded-full h-2 overflow-hidden border" style={{ backgroundColor: 'var(--bg-hover)', borderColor: 'var(--border-default)' }}>
                            <div 
                              className="h-full rounded-full transition-all duration-500 ease-out" 
                              style={{ width: `${p.total_tasks ? (p.completed_tasks / p.total_tasks * 100) : 0}%`, backgroundColor: 'var(--primary)' }} 
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
              <div className="py-12 text-center flex flex-col items-center gap-2" style={{ color: 'var(--text-tertiary)' }}>
                <Info size={32} strokeWidth={1} />
                <p>Нет активных проектов</p>
              </div>
            )}
          </Card>
        </div>

        {/* SIDEBAR WIDGETS */}
        <div className="space-y-6">
          <DailyQuestWidget />
          
          <Card className="overflow-hidden relative group" style={{ backgroundColor: 'var(--bg-surface-2)', borderColor: 'var(--border-default)' }}>
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity" style={{ color: 'var(--primary)' }}>
              <TrendingUp size={80} />
            </div>
            <div className="relative z-10">
              <h3 className="font-bold text-lg mb-2 text-primary-token">Общая эффективность</h3>
              <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>Средний SPI по всем проектам вырос на 4.2% за прошлую неделю.</p>
              <Button variant="outline" size="sm" className="w-full" style={{ backgroundColor: 'rgba(255,255,255,0.1)', borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}>
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
    docs: { bg: 'var(--accent-docs-light)', text: 'var(--accent-docs)', border: 'var(--accent-docs)' },
    engineering: { bg: 'var(--accent-engineering-light)', text: 'var(--accent-engineering)', border: 'var(--accent-engineering)' },
    audit: { bg: 'var(--accent-audit-light)', text: 'var(--accent-audit)', border: 'var(--accent-audit)' },
    success: { bg: 'var(--success-light)', text: 'var(--success)', border: 'var(--success)' },
    leaders: { bg: 'var(--accent-leaders-light)', text: 'var(--accent-leaders)', border: 'var(--accent-leaders)' },
    production: { bg: 'var(--accent-production-light)', text: 'var(--accent-production)', border: 'var(--accent-production)' },
    approvals: { bg: 'var(--accent-approvals-light)', text: 'var(--accent-approvals)', border: 'var(--accent-approvals)' },
  };

  const theme = colors[color] || colors.docs;

  return (
    <Card 
      className="border shadow-sm transition-all hover:shadow-md hover:-translate-y-1 surface-card"
      padding="sm"
      style={{ backgroundColor: theme.bg, borderColor: theme.border }}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider opacity-70" style={{ color: theme.text }}>{label}</p>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-black" style={{ color: theme.text }}>{value}</span>
          </div>
          <p className="text-[10px] font-medium opacity-60 mt-1 italic" style={{ color: theme.text }}>{desc}</p>
        </div>
        <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(255,255,255,0.5)' }}>
          <Icon size={24} strokeWidth={2.5} style={{ color: theme.text }} />
        </div>
      </div>
    </Card>
  );
}
