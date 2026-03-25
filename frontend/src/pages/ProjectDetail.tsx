import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getProjectHealth, getEngineerSPI } from '../api/dashboard';
import { getProjectTasks } from '../api/tasks';
import type { ProjectHealth, Task, EngineerSPI } from '../types';
import StatusBadge from '../components/StatusBadge';
import SPIIndicator from '../components/SPIIndicator';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity, FileText, ListTodo, BarChart3, Shield } from 'lucide-react';

const TABS = [
  { id: 'overview', label: 'Обзор', icon: Activity },
  { id: 'tasks', label: 'Задачи', icon: ListTodo },
  { id: 'gantt', label: 'Gantt', icon: BarChart3 },
  { id: 'health', label: 'Здоровье', icon: Shield },
];

export default function ProjectDetail() {
  const { id } = useParams();
  const [tab, setTab] = useState('overview');
  const [health, setHealth] = useState<ProjectHealth | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [engineers, setEngineers] = useState<EngineerSPI[]>([]);

  useEffect(() => {
    if (id) {
      const pid = Number(id);
      getProjectHealth(pid).then(setHealth).catch(() => {});
      getProjectTasks(pid).then(setTasks).catch(() => {});
      getEngineerSPI(pid).then(setEngineers).catch(() => {});
    }
  }, [id]);

  return (
    <div>
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h1 className="text-2xl font-bold">{health?.project.name || `Проект #${id}`}</h1>
        <p className="text-gray-500">{health?.project.number || ''}</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white rounded-xl shadow-sm p-1">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t.id ? 'bg-primary-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && health && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="SPI" value={health.spi?.toFixed(2) || '—'} color={health.risk_level === 'low' ? 'green' : health.risk_level === 'medium' ? 'yellow' : 'red'} />
          <MetricCard label="Всего задач" value={String(health.total_tasks)} color="blue" />
          <MetricCard label="Завершено" value={String(health.completed_tasks)} color="green" />
          <MetricCard label="Просрочено" value={String(health.overdue_tasks)} color="red" />
        </div>
      )}

      {tab === 'tasks' && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Задача</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Статус</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Инженер</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Прогресс</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {tasks.map(t => (
                <tr key={t.id} className={`hover:bg-gray-50 ${t.is_critical ? 'border-l-4 border-red-500' : ''}`}>
                  <td className="px-6 py-4 font-medium">{t.title}</td>
                  <td className="px-6 py-4"><StatusBadge status={t.status} /></td>
                  <td className="px-6 py-4 text-sm text-gray-600">{t.engineer || '—'}</td>
                  <td className="px-6 py-4 text-sm">{t.percent_complete}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'gantt' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="font-semibold mb-4">Gantt-диаграмма</h2>
          <div className="space-y-2">
            {tasks.map(t => {
              const startDay = t.es || 0;
              const duration = (t.ef || 1) - startDay;
              return (
                <div key={t.id} className="flex items-center gap-3">
                  <div className="w-48 text-sm truncate">{t.title}</div>
                  <div className="flex-1 relative h-6 bg-gray-100 rounded">
                    <div
                      className={`absolute h-6 rounded ${t.is_critical ? 'bg-red-500' : 'bg-primary-500'}`}
                      style={{ left: `${startDay * 5}%`, width: `${Math.max(duration * 5, 3)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {tab === 'health' && (
        <div>
          <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="font-semibold mb-4">SPI по инженерам</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={engineers}>
                <XAxis dataKey="engineer" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 1.5]} />
                <Tooltip />
                <Bar dataKey="spi">
                  {engineers.map((e, i) => (
                    <Cell key={i} fill={e.spi && e.spi >= 0.95 ? '#16a34a' : e.spi && e.spi >= 0.8 ? '#eab308' : '#dc2626'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="font-semibold mb-2">Общий статус</h2>
            <StatusBadge status={health?.risk_level || 'low'} />
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    yellow: 'bg-yellow-50 text-yellow-700',
    red: 'bg-red-50 text-red-700',
  };
  return (
    <div className={`rounded-xl p-5 ${colors[color] || colors.blue}`}>
      <div className="text-sm font-medium opacity-75">{label}</div>
      <div className="text-3xl font-bold mt-1">{value}</div>
    </div>
  );
}
