import { useState, useRef, useCallback, useEffect } from 'react';
import { Button, Badge } from '../components/ui';
import { Search, Plus, Filter } from 'lucide-react';

// Типы данных
interface Project {
  id: string;
  code: string;
  name: string;
  customer: string;
  status: 'active' | 'archived';
  documentsCount: number;
  createdAt: string;
  archivedAt?: string;
}

interface ColumnWidth {
  code: number;
  name: number;
  customer: number;
  status: number;
  documentsCount: number;
  createdAt: number;
  archivedAt: number;
}

const DEFAULT_COLUMN_WIDTHS: ColumnWidth = {
  code: 100,
  name: 250,
  customer: 200,
  status: 120,
  documentsCount: 100,
  createdAt: 120,
  archivedAt: 120,
};

// Мок-данные (временно, пока нет API)
const mockProjects: Project[] = [
  { id: '1', code: 'PRJ-001', name: 'Завод "Альфа"', customer: 'ООО "Альфа-Строй"', status: 'active', documentsCount: 142, createdAt: '2025-01-15', archivedAt: undefined },
  { id: '2', code: 'PRJ-002', name: 'Мост через реку К', customer: 'ФКУ "Упрдор"', status: 'archived', documentsCount: 89, createdAt: '2024-03-20', archivedAt: '2026-03-05' },
  { id: '3', code: 'PRJ-003', name: 'ЖК "Северный"', customer: 'АО "ПИК"', status: 'active', documentsCount: 256, createdAt: '2025-06-10', archivedAt: undefined },
  { id: '4', code: 'PRJ-004', name: 'Трасса М-12', customer: 'ГК "Автодор"', status: 'active', documentsCount: 178, createdAt: '2025-02-01', archivedAt: undefined },
  { id: '5', code: 'PRJ-005', name: 'Нефтеперерабатывающий завод', customer: 'ПАО "НК Роснефть"', status: 'active', documentsCount: 423, createdAt: '2024-11-20', archivedAt: undefined },
];

type ColumnKey = keyof ColumnWidth;

interface SortConfig {
  column: keyof Project | 'customer' | 'documentsCount';
  direction: 'asc' | 'desc';
}

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'archived'>('all');
  const [projects] = useState<Project[]>(mockProjects);
  const [columnWidths, setColumnWidths] = useState<ColumnWidth>(() => {
    const saved = localStorage.getItem('iris-projects-column-widths');
    return saved ? JSON.parse(saved) : DEFAULT_COLUMN_WIDTHS;
  });
  const [resizingColumn, setResizingColumn] = useState<ColumnKey | null>(null);
  const [startX, setStartX] = useState(0);
  const [startWidth, setStartWidth] = useState(0);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ column: 'createdAt', direction: 'desc' });
  const [scale, setScale] = useState(100);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const tableRef = useRef<HTMLTableElement>(null);

  // Сохранение ширины колонок в localStorage
  const updateColumnWidth = useCallback((column: ColumnKey, width: number) => {
    const newWidths = { ...columnWidths, [column]: Math.max(80, width) };
    setColumnWidths(newWidths);
    localStorage.setItem('iris-projects-column-widths', JSON.stringify(newWidths));
  }, [columnWidths]);

  // Начало перетаскивания
  const handleResizeStart = useCallback((e: React.MouseEvent, column: ColumnKey) => {
    e.preventDefault();
    e.stopPropagation();
    setResizingColumn(column);
    setStartX(e.clientX);
    setStartWidth(columnWidths[column]);
    document.body.style.cursor = 'col-resize';
  }, [columnWidths]);

  // Перетаскивание
  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!resizingColumn) return;
    const diff = e.clientX - startX;
    const newWidth = startWidth + diff;
    updateColumnWidth(resizingColumn, newWidth);
  }, [resizingColumn, startX, startWidth, updateColumnWidth]);

  // Конец перетаскивания
  const handleResizeEnd = useCallback(() => {
    setResizingColumn(null);
    document.body.style.cursor = '';
  }, []);

  // Добавление глобальных обработчиков
  useEffect(() => {
    if (resizingColumn) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      return () => {
        window.removeEventListener('mousemove', handleResizeMove);
        window.removeEventListener('mouseup', handleResizeEnd);
      };
    }
  }, [resizingColumn, handleResizeMove, handleResizeEnd]);

  // Фильтрация проектов
  const filteredProjects = projects.filter(project => {
    const searchLower = searchQuery.toLowerCase();
    
    // Поиск по всем колонкам
    const matchesCode = project.code.toLowerCase().includes(searchLower);
    const matchesName = project.name.toLowerCase().includes(searchLower);
    const matchesCustomer = project.customer.toLowerCase().includes(searchLower);
    const matchesCreatedAt = project.createdAt.includes(searchQuery);
    const matchesArchivedAt = project.archivedAt?.includes(searchQuery) || false;
    
    // Фильтр по статусу
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    
    // Если поиск пустой, показываем всё с учётом статуса
    if (searchQuery === '') return matchesStatus;
    
    // Если поиск есть, ищем по всем полям + статус
    return matchesStatus && (
      matchesCode || 
      matchesName || 
      matchesCustomer || 
      matchesCreatedAt || 
      matchesArchivedAt
    );
  });

  // Обработчик клика на заголовок колонки
  const handleSort = (column: keyof Project | 'customer' | 'documentsCount') => {
    setSortConfig(prev => ({
      column,
      direction: prev.column === column && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Сортировка проектов
  const filteredAndSortedProjects = [...filteredProjects].sort((a, b) => {
    const { column, direction } = sortConfig;
    const multiplier = direction === 'asc' ? 1 : -1;

    let aValue: any = a[column];
    let bValue: any = b[column];

    // Обработка undefined значений
    if (aValue === undefined) aValue = '';
    if (bValue === undefined) bValue = '';

    // Сортировка по датам
    if (column === 'createdAt' || column === 'archivedAt') {
      return multiplier * (new Date(aValue).getTime() - new Date(bValue).getTime());
    }

    // Сортировка по числам
    if (column === 'documentsCount') {
      return multiplier * (aValue - bValue);
    }

    // Сортировка по строкам (с учётом русского языка)
    return multiplier * String(aValue).localeCompare(String(bValue), 'ru-RU');
  });

  // Пагинация
  const totalPages = Math.ceil(filteredAndSortedProjects.length / itemsPerPage);
  const paginatedProjects = filteredAndSortedProjects.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Обработчики пагинации
  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToPrevious = () => goToPage(currentPage - 1);
  const goToNext = () => goToPage(currentPage + 1);

  // Компонент для изменения размера колонки
  const Resizer = ({ column }: { column: ColumnKey }) => (
    <div
      className="absolute right-0 top-0 bottom-0 w-2 cursor-col-resize hover:bg-[var(--primary)] active:bg-[var(--primary-hover)] transition-colors z-20 flex items-center justify-center"
      onMouseDown={(e) => handleResizeStart(e, column)}
      role="separator"
      aria-valuenow={columnWidths[column]}
      title="Изменить размер колонки"
    >
      <div className="w-0.5 h-4 bg-[var(--border)] rounded opacity-0 hover:opacity-100 transition-opacity" />
    </div>
  );

  // Компонент индикатора сортировки
  const SortIcon = ({ column }: { column: keyof Project | 'customer' | 'documentsCount' }) => {
    if (sortConfig.column !== column) {
      return <span className="ml-2 text-[var(--text-disabled)] opacity-0 group-hover:opacity-50 text-xs">⇅</span>;
    }
    return (
      <span className="ml-2 text-[var(--primary)] text-xs font-bold">
        {sortConfig.direction === 'asc' ? '↑' : '↓'}
      </span>
    );
  };

  // Обработчик клика на заголовок
  const HeaderCell = ({ 
    column, 
    children,
    className = ''
  }: { 
    column: keyof Project | 'customer' | 'documentsCount';
    children: React.ReactNode;
    className?: string;
  }) => (
    <th
      className={`text-left py-3 px-4 text-sm font-medium text-[var(--text-muted)] relative select-none cursor-pointer hover:bg-[var(--bg-hover)] transition-colors group ${className}`}
      style={{ width: columnWidths[column as ColumnKey] }}
      onClick={() => handleSort(column)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center flex-1">
          {children}
          <SortIcon column={column} />
        </div>
      </div>
      <Resizer column={column as ColumnKey} />
    </th>
  );

  return (
    <div className="max-w-7xl mx-auto">
      {/* Заголовок страницы */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-[var(--text-base)]">
            Портфель проектов
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            Управление проектами и документацией
          </p>
        </div>
        <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
          Создать проект
        </Button>
      </div>

        {/* Поиск и фильтры */}
        <div className="card mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Поиск */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="text"
                placeholder="Поиск по всем полям..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-base)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--primary)] transition-colors"
              />
            </div>

            {/* Фильтры */}
            <div className="flex gap-2">
              <div className="relative">
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as typeof statusFilter)}
                  className="appearance-none pl-4 pr-10 py-2 bg-[var(--bg-card)] border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-base)] focus:outline-none focus:border-[var(--primary)] cursor-pointer transition-colors"
                >
                  <option value="all">Все статусы</option>
                  <option value="active">Активные</option>
                  <option value="archived">Архив</option>
                </select>
                <Filter className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)] pointer-events-none" />
              </div>

              <Button variant="secondary" size="md">
                Сбросить
              </Button>
            </div>
          </div>
        </div>

        {/* Таблица проектов */}
        <div className="card overflow-hidden">
          <div 
            className="overflow-x-auto transition-transform duration-200 origin-top-left"
            style={{ transform: `scale(${scale / 100})`, minHeight: '400px' }}
          >
            <table ref={tableRef} className="w-full table-fixed" style={{ minWidth: '100%' }}>
              <thead>
                <tr className="border-b border-[var(--border)]">
                  <HeaderCell column="code">Код</HeaderCell>
                  <HeaderCell column="name">Название</HeaderCell>
                  <HeaderCell column="customer">Заказчик</HeaderCell>
                  <HeaderCell column="status">Статус</HeaderCell>
                  <HeaderCell column="documentsCount" className="text-center">Документы</HeaderCell>
                  <HeaderCell column="createdAt">Создан</HeaderCell>
                  <HeaderCell column="archivedAt">Завершён</HeaderCell>
                </tr>
              </thead>
              <tbody>
                {paginatedProjects.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-[var(--text-muted)]">
                      Проекты не найдены
                    </td>
                  </tr>
                ) : (
                  paginatedProjects.map((project) => (
                    <tr
                      key={project.id}
                      className="border-b border-[var(--border-light)] hover:bg-[var(--bg-hover)] cursor-pointer transition-colors"
                      onClick={() => window.location.href = `/projects/${project.id}/documents`}
                    >
                      <td className="py-3 px-4 text-sm font-mono text-[var(--text-base)]">
                        {project.code}
                      </td>
                      <td className="py-3 px-4 text-sm text-[var(--text-base)]">
                        {project.name}
                      </td>
                      <td className="py-3 px-4 text-sm text-[var(--text-muted)]">
                        {project.customer}
                      </td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={project.status === 'active' ? 'success' : 'neutral'}
                          leftIcon={
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              project.status === 'active' ? 'bg-[var(--success)]' : 'bg-[var(--text-muted)]'
                            }`} />
                          }
                        >
                          {project.status === 'active' ? 'Активен' : 'Архив'}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-center text-[var(--text-muted)]">
                        {project.documentsCount}
                      </td>
                      <td className="py-3 px-4 text-sm text-[var(--text-muted)]">
                        {new Date(project.createdAt).toLocaleDateString('ru-RU')}
                      </td>
                      <td className="py-3 px-4 text-sm text-[var(--text-muted)]">
                        {project.archivedAt ? new Date(project.archivedAt).toLocaleDateString('ru-RU') : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan={7} className="py-3 px-4 border-t border-[var(--border)] bg-[var(--bg-card)]">
                    <nav 
                      className="flex items-center justify-between"
                      aria-label="Пагинация проектов"
                    >
                      <div className="flex items-center gap-2">
                        <button
                          onClick={goToPrevious}
                          disabled={currentPage === 1}
                          className="px-3 py-1.5 text-sm rounded-md border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-base)] hover:bg-[var(--bg-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          aria-label="Предыдущая страница"
                        >
                          Назад
                        </button>
                        <span 
                          className="px-4 py-1.5 text-sm font-medium text-[var(--text-base)] min-w-[140px] text-center"
                          aria-current="page"
                        >
                          Страница {currentPage} из {totalPages || 1}
                        </span>
                        <button
                          onClick={goToNext}
                          disabled={currentPage === totalPages || totalPages === 0}
                          className="px-3 py-1.5 text-sm rounded-md border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-base)] hover:bg-[var(--bg-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          aria-label="Следующая страница"
                        >
                          Вперёд
                        </button>
                      </div>

                      {/* Масштабирование */}
                      <div className="flex items-center gap-2" role="group" aria-label="Масштабирование таблицы">
                        <button
                          onClick={() => setScale(prev => Math.max(50, prev - 10))}
                          className="w-8 h-8 flex items-center justify-center rounded-md border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-base)] hover:bg-[var(--bg-hover)] hover:text-[var(--primary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          title="Уменьшить"
                          disabled={scale <= 50}
                          aria-label="Уменьшить масштаб"
                        >
                          <span className="text-lg font-bold leading-none">−</span>
                        </button>
                        <span 
                          className="text-sm text-[var(--text-muted)] min-w-[50px] text-center font-medium"
                          aria-label={`Масштаб ${scale} процентов`}
                        >
                          {scale}%
                        </span>
                        <button
                          onClick={() => setScale(prev => Math.min(150, prev + 10))}
                          className="w-8 h-8 flex items-center justify-center rounded-md border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-base)] hover:bg-[var(--bg-hover)] hover:text-[var(--primary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          title="Увеличить"
                          disabled={scale >= 150}
                          aria-label="Увеличить масштаб"
                        >
                          <span className="text-lg font-bold leading-none">+</span>
                        </button>
                      </div>
                    </nav>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
  );
}
