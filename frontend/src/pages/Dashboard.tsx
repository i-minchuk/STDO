import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPortfolio } from '../api/projects';
import type { Project, PortfolioSummary } from '../types';
import StatusBadge from '../components/StatusBadge';
import SPIIndicator from '../components/SPIIndicator';
import DailyQuestWidget from '../components/DailyQuestWidget';
import { FolderOpen, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

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

  const cards = [
    { label: 'Всего проектов', value: summary.total, icon: FolderOpen, color: 'bg-primary-50 text-primary-700' },
    { label: 'Активных', value: summary.active, icon: Clock, color: 'bg-blue-50 text-blue-700' },
    { label: 'В зоне риска', value: summary.at_risk, icon: AlertTriangle, color: 'bg-red-50 text-red-700' },
    { label: 'Завершено', value: summary.completed, icon: CheckCircle, color: 'bg-green-50 text-green-700' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Портфолио проектов</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className={`rounded-xl p-5 ${color}`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium opacity-75">{label}</div>
                <div className="text-3xl font-bold mt-1">{value}</div>
              </div>
              <Icon size={32} className="opacity-50" />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2"></div>
        <DailyQuestWidget />
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Проект</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Заказчик</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Статус</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Прогресс</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">SPI</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Риск</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {projects.map(p => (
              <tr key={p.id} onClick={() => navigate(`/projects/${p.id}`)} className="hover:bg-gray-50 cursor-pointer transition-colors">
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900">{p.name}</div>
                  <div className="text-sm text-gray-500">{p.number}</div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{p.customer}</td>
                <td className="px-6 py-4"><StatusBadge status={p.status} /></td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div className="bg-primary-600 h-2 rounded-full" style={{ width: `${p.total_tasks ? (p.completed_tasks / p.total_tasks * 100) : 0}%` }} />
                    </div>
                    <span className="text-sm text-gray-600">{p.completed_tasks}/{p.total_tasks}</span>
                  </div>
                </td>
                <td className="px-6 py-4"><SPIIndicator value={p.spi} /></td>
                <td className="px-6 py-4"><StatusBadge status={p.risk_level} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
