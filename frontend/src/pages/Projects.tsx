import { FolderKanban, CalendarDays, Users, ArrowRight, Clock3 } from 'lucide-react';
import { Link } from 'react-router-dom';

const mockProjects = [
  {
    id: 1,
    code: 'STDO-001',
    name: 'ДокПоток IRIS',
    status: 'В работе',
    stage: 'Разработка',
    team: 'Платформа',
    deadline: '30.04.2026',
  },
  {
    id: 2,
    code: 'NPP-KM',
    name: 'Конструкции НПЗ',
    status: 'На проверке',
    stage: 'Согласование',
    team: 'КМ / КЖ',
    deadline: '18.04.2026',
  },
  {
    id: 3,
    code: 'MDR-EXCEL',
    name: 'Импорт реестров и MDR',
    status: 'В работе',
    stage: 'Тестирование',
    team: 'Backend + Frontend',
    deadline: '22.04.2026',
  },
];

function statusClasses(status: string) {
  switch (status) {
    case 'В работе':
      return 'bg-blue-50 text-blue-700 border-blue-200';
    case 'На проверке':
      return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'Завершён':
      return 'bg-green-50 text-green-700 border-green-200';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200';
  }
}

export default function Projects() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Проекты</h1>
          <p className="mt-1 text-sm text-gray-500">
            Общий список проектных потоков, команд и текущих этапов работ.
          </p>
        </div>

        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white no-underline hover:bg-primary-700"
        >
          На дашборд
          <ArrowRight size={16} />
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-3 text-blue-600">
              <FolderKanban size={20} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Всего проектов</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-amber-50 p-3 text-amber-600">
              <Clock3 size={20} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Активные</p>
              <p className="text-2xl font-bold text-gray-900">7</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-50 p-3 text-emerald-600">
              <Users size={20} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Команд</p>
              <p className="text-2xl font-bold text-gray-900">5</p>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200 px-5 py-4">
          <h2 className="text-lg font-semibold text-gray-900">Список проектов</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {mockProjects.map((project) => (
            <div
              key={project.id}
              className="flex flex-col gap-4 px-5 py-4 lg:flex-row lg:items-center lg:justify-between"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-3">
                  <h3 className="text-base font-semibold text-gray-900">{project.name}</h3>
                  <span
                    className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${statusClasses(project.status)}`}
                  >
                    {project.status}
                  </span>
                </div>

                <div className="mt-2 flex flex-wrap gap-4 text-sm text-gray-500">
                  <span className="font-mono text-gray-700">{project.code}</span>
                  <span className="inline-flex items-center gap-1">
                    <CalendarDays size={14} />
                    Срок: {project.deadline}
                  </span>
                  <span>Этап: {project.stage}</span>
                  <span>Команда: {project.team}</span>
                </div>
              </div>

              <div>
                <Link
                  to="/documents"
                  className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 no-underline hover:bg-gray-50"
                >
                  Открыть документы
                  <ArrowRight size={16} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}