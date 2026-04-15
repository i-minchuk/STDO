import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPortfolio } from '../api/projects';
import type { Project, PortfolioSummary } from '../types';
import StatusBadge from '../components/StatusBadge';
import SPIIndicator from '../components/SPIIndicator';
import DailyQuestWidget from '../components/DailyQuestWidget';
import {
  FolderOpen,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowUpRight,
} from 'lucide-react';
import { Card, Button } from '../components/ui';

type StatColor = 'docs' | 'leaders' | 'audit' | 'engineering';

const MOCK_SUMMARY: PortfolioSummary = {
  total: 5,
  active: 3,
  at_risk: 1,
  completed: 1,
};

const MOCK_PROJECTS: Project[] = [
  {
    id: 1,
    code: 'PRJ-001',
    name: 'Модернизация НПЗ',
    status: 'active',
    customer: 'Газпром',
    start_date: '2026-01-15',
    end_date_plan: '2026-12-31',
    total_tasks: 45,
    completed_tasks: 28,
    spi: 0.92,
    risk_level: 'medium',
  },
  {
    id: 2,
    code: 'PRJ-002',
    name: 'Строительство ЛЭП',
    status: 'active',
    customer: 'РусГидро',
    start_date: '2026-02-01',
    end_date_plan: '2026-09-30',
    total_tasks: 30,
    completed_tasks: 25,
    spi: 1.05,
    risk_level: 'low',
  },
  {
    id: 3,
    code: 'PRJ-003',
    name: 'Реконструкция котельной',
    status: 'active',
    customer: 'ТГК-1',
    start_date: '2026-03-01',
    end_date_plan: '2026-11-15',
    total_tasks: 20,
    completed_tasks: 5,
    spi: 0.62,
    risk_level: 'high',
  },
];

function normalizeSummary(input: PortfolioSummary | null | undefined): PortfolioSummary {
  const raw = (input ?? {}) as Partial<PortfolioSummary>;

  return {
    total: Number(raw.total ?? 0),
    active: Number(raw.active ?? 0),
    at_risk: Number(raw.at_risk ?? 0),
    completed: Number(raw.completed ?? 0),
  };
}

function normalizeProjects(input: Project[] | null | undefined): Project[] {
  if (!Array.isArray(input)) return MOCK_PROJECTS;

  return input.map((item, index) => {
    const raw = (item ?? {}) as Partial<Project>;

    return {
      id: raw.id ?? index,
      code: raw.code ?? '—',
      name: raw.name ?? `Проект ${index + 1}`,
      status: raw.status ?? 'active',
      customer: raw.customer ?? '—',
      start_date: raw.start_date ?? '',
      end_date_plan: raw.end_date_plan ?? '',
      total_tasks: raw.total_tasks ?? 0,
      completed_tasks: raw.completed_tasks ?? 0,
      spi: raw.spi ?? 0,
      risk_level: raw.risk_level ?? 'low',
    } as Project;
  });
}

export default function Dashboard() {
  const [summary, setSummary] = useState<PortfolioSummary>(MOCK_SUMMARY);
  const [projects, setProjects] = useState<Project[]>(MOCK_PROJECTS);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;

    getPortfolio()
      .then((d) => {
        if (!mounted) return;

        const nextSummary = normalizeSummary(d?.summary);
        const nextProjects = normalizeProjects(d?.projects);

        setSummary(nextSummary);
        setProjects(nextProjects);
        setLoadError(null);
      })
      .catch((err) => {
        if (!mounted) return;

        setSummary(MOCK_SUMMARY);
        setProjects(MOCK_PROJECTS);
        setLoadError(
          err?.message ??
            'Не удалось загрузить данные портфеля. Показаны примерные значения.'
        );
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const safeSummary = useMemo(
    () => normalizeSummary(summary ?? MOCK_SUMMARY),
    [summary]
  );
  const safeProjects = useMemo(
    () => normalizeProjects(projects ?? MOCK_PROJECTS),
    [projects]
  );

  const stats: Array<{
    label: string;
    value: number;
    icon: typeof FolderOpen;
    color: StatColor;
    desc: string;
  }> = [
    {
      label: 'Всего проектов',
      value: safeSummary.total ?? 0,
      icon: FolderOpen,
      color: 'docs',
      desc: 'За всё время',
    },
    {
      label: 'Активных',
      value: safeSummary.active ?? 0,
      icon: Clock,
      color: 'leaders',
      desc: 'В разработке',
    },
    {
      label: 'В зоне риска',
      value: safeSummary.at_risk ?? 0,
      icon: AlertTriangle,
      color: 'audit',
      desc: 'Требуют внимания',
    },
    {
      label: 'Завершено',
      value: safeSummary.completed ?? 0,
      icon: CheckCircle,
      color: 'engineering',
      desc: 'Успешно закрыты',
    },
  ];

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Портфолио проектов
          </h1>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Обзор состояния проектов на{' '}
            {new Date().toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </p>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" size="sm">
            Аналитика
          </Button>
          <Button size="sm" onClick={() => navigate('/documents/new')}>
            + Добавить проект
          </Button>
        </div>
      </section>

      {loadError && (
        <Card className="border border-amber-500/25 bg-amber-500/10 px-4 py-3 text-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 text-amber-300" />
            <div>
              <div className="font-medium text-amber-100">
                Данные загружены с резервными значениями
              </div>
              <p className="mt-1 text-xs text-amber-100/80">{loadError}</p>
            </div>
          </div>
        </Card>
      )}

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((s) => (
          <StatCard
            key={s.label}
            label={s.label}
            value={s.value}
            icon={s.icon}
            color={s.color}
            desc={s.desc}
          />
        ))}
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1.6fr_0.9fr]">
        <Card className="p-0 overflow-hidden">
          <div
            className="flex items-center justify-between border-b px-5 py-4"
            style={{ borderColor: 'var(--border-default)' }}
          >
            <div>
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Последние проекты
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Актуальный статус проектного портфеля
              </p>
            </div>

            <Button variant="ghost" size="sm" onClick={() => navigate('/documents')}>
              Все проекты
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead style={{ backgroundColor: 'var(--bg-surface-2)' }}>
                <tr>
                  <th
                    className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    Проект
                  </th>
                  <th
                    className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    Заказчик
                  </th>
                  <th
                    className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    Прогресс
                  </th>
                  <th
                    className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    SPI
                  </th>
                  <th
                    className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    Риск
                  </th>
                </tr>
              </thead>

              <tbody>
                {loading ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-5 py-6 text-sm"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      Загрузка данных...
                    </td>
                  </tr>
                ) : safeProjects.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-5 py-10 text-center text-sm"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      Нет активных проектов
                    </td>
                  </tr>
                ) : (
                  safeProjects.map((p) => {
                    const totalTasks = p.total_tasks ?? 0;
                    const completedTasks = p.completed_tasks ?? 0;
                    const progress = Math.round(
                      totalTasks ? (completedTasks / totalTasks) * 100 : 0
                    );

                    return (
                      <tr
                        key={p.id}
                        onClick={() => navigate(`/projects/${p.id}`)}
                        className="cursor-pointer transition-colors"
                        style={{ borderTop: '1px solid var(--border-light)' }}
                      >
                        <td className="px-5 py-4">
                          <div className="font-medium" style={{ color: 'var(--text-primary)' }}>
                            {p.name}
                          </div>
                          <div
                            className="mt-1 text-xs font-mono"
                            style={{ color: 'var(--text-tertiary)' }}
                          >
                            {p.code}
                          </div>
                        </td>

                        <td
                          className="px-5 py-4 text-sm"
                          style={{ color: 'var(--text-secondary)' }}
                        >
                          {p.customer}
                        </td>

                        <td className="px-5 py-4">
                          <div className="text-sm" style={{ color: 'var(--text-primary)' }}>
                            Задачи
                          </div>
                          <div
                            className="mt-1 text-xs"
                            style={{ color: 'var(--text-secondary)' }}
                          >
                            {progress}%
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <SPIIndicator value={p.spi} />
                        </td>

                        <td className="px-5 py-4">
                          <StatusBadge status={p.risk_level} />
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              Общая эффективность
            </h3>
            <p
              className="mt-2 text-sm leading-6"
              style={{ color: 'var(--text-secondary)' }}
            >
              Средний SPI по всем проектам вырос на 4.2% за прошлую неделю.
            </p>
            <div className="mt-4">
              <Button variant="outline" size="sm" className="w-full">
                <span className="inline-flex items-center gap-2">
                  Смотреть отчет
                  <ArrowUpRight size={14} />
                </span>
              </Button>
            </div>
          </Card>

          <DailyQuestWidget />
        </div>
      </section>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
  color,
  desc,
}: {
  label: string;
  value: number;
  icon: typeof FolderOpen;
  color: StatColor;
  desc: string;
}) {
  const accentMap: Record<StatColor, string> = {
    docs: 'var(--accent-docs)',
    leaders: 'var(--accent-leaders)',
    audit: 'var(--accent-audit)',
    engineering: 'var(--accent-engineering)',
  };

  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <div
            className="text-sm font-medium"
            style={{ color: 'var(--text-secondary)' }}
          >
            {label}
          </div>
          <div
            className="mt-3 text-3xl font-bold"
            style={{ color: 'var(--text-primary)' }}
          >
            {value}
          </div>
          <div
            className="mt-2 text-sm"
            style={{ color: 'var(--text-tertiary)' }}
          >
            {desc}
          </div>
        </div>

        <div
          className="flex h-11 w-11 items-center justify-center rounded-xl"
          style={{
            backgroundColor: 'var(--bg-surface-2)',
            color: accentMap[color],
            border: '1px solid var(--border-default)',
          }}
        >
          <Icon size={20} />
        </div>
      </div>
    </Card>
  );
}