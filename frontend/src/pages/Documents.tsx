import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDocuments } from '../api/documents';
import type { Document } from '../types';
import { Search, FileText, Plus, ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Info } from 'lucide-react';
import { Badge, Button, Card, Input, Select } from '../components/ui';

// --- Helper functions for Status Badge (copied from DocumentDetail.tsx for consistency) ---
const STATUS_BADGE_VARIANTS: Record<string, 'gray' | 'blue' | 'green' | 'yellow' | 'red' | 'indigo'> = {
  active: 'green',
  in_progress: 'blue',
  completed: 'gray',
  not_started: 'gray',
  on_review: 'yellow',
  approved: 'green',
  draft: 'gray',
  archived: 'gray',
  low: 'green',
  medium: 'yellow',
  high: 'red',
  superseded: 'gray',
};

const STATUS_BADGE_LABELS: Record<string, string> = {
  active: 'Активный',
  in_progress: 'В работе',
  completed: 'Завершён',
  not_started: 'Не начата',
  on_review: 'На проверке',
  approved: 'Утверждён',
  draft: 'Черновик',
  archived: 'Архив',
  low: 'Низкий',
  medium: 'Средний',
  high: 'Высокий',
  superseded: 'Замещен',
};

function mapStatusToBadgeVariant(status: string): 'gray' | 'blue' | 'green' | 'yellow' | 'red' | 'indigo' {
  return STATUS_BADGE_VARIANTS[status] || 'gray';
}

function mapStatusToBadgeLabel(status: string): string {
  return STATUS_BADGE_LABELS[status] || status;
}
// -----------------------------------------------------------------------------------------

const MOCK_DOCS: Document[] = [
  { id: 1, code: 'НПЗ-КМ-001', title: 'Общий вид конструкций', project_id: 1, status: 'approved', doc_type: 'КМ', current_revision_id: 3, discipline: 'КМ', created_at: new Date('2026-01-15T10:00:00Z') },
  { id: 2, code: 'НПЗ-КМ-002', title: 'Узлы сопряжения', project_id: 1, status: 'on_review', doc_type: 'КМ', current_revision_id: 5, discipline: 'КМ', created_at: new Date('2026-02-01T10:00:00Z') },
  { id: 3, code: 'ЛЭП-ЭС-001', title: 'Схема электроснабжения', project_id: 2, status: 'draft', doc_type: 'ЭС', current_revision_id: null, discipline: 'ЭС', created_at: new Date('2026-03-10T10:00:00Z') },
  { id: 4, code: 'КОТ-ТМ-001', title: 'Тепломеханические решения', project_id: 3, status: 'in_progress', doc_type: 'ТМ', current_revision_id: 2, discipline: 'ТМ', created_at: new Date('2026-03-05T10:00:00Z') },
  { id: 5, code: 'НПЗ-АР-003', title: 'Архитектурные решения', project_id: 1, status: 'approved', doc_type: 'АР', current_revision_id: 7, discipline: 'АР', created_at: new Date('2026-01-20T10:00:00Z') },
  { id: 6, code: 'ЛЭП-ПС-002', title: 'План силовой сети', project_id: 2, status: 'on_review', doc_type: 'ПС', current_revision_id: 8, discipline: 'ПС', created_at: new Date('2026-02-15T10:00:00Z') },
  { id: 7, code: 'НПЗ-КМ-003', title: 'Фундаменты', project_id: 1, status: 'draft', doc_type: 'КМ', current_revision_id: null, discipline: 'КМ', created_at: new Date('2026-03-01T10:00:00Z') },
  { id: 8, code: 'КОТ-ОВ-002', title: 'Вентиляция', project_id: 3, status: 'in_progress', doc_type: 'ОВ', current_revision_id: 4, discipline: 'ОВ', created_at: new Date('2026-03-20T10:00:00Z') },
  { id: 9, code: 'ЛЭП-ЭС-003', title: 'Кабельный журнал', project_id: 2, status: 'approved', doc_type: 'ЭС', current_revision_id: 6, discipline: 'ЭС', created_at: new Date('2026-02-28T10:00:00Z') },
  { id: 10, code: 'НПЗ-ТХ-004', title: 'Технологическая схема', project_id: 1, status: 'on_review', doc_type: 'ТХ', current_revision_id: 9, discipline: 'ТХ', created_at: new Date('2026-01-25T10:00:00Z') },
  { id: 11, code: 'КОТ-ВК-001', title: 'Водоснабжение и канализация', project_id: 3, status: 'draft', doc_type: 'ВК', current_revision_id: null, discipline: 'ВК', created_at: new Date('2026-03-12T10:00:00Z') },
  { id: 12, code: 'ЛЭП-АР-004', title: 'Разрез по оси 1-1', project_id: 2, status: 'in_progress', doc_type: 'АР', current_revision_id: 10, discipline: 'АР', created_at: new Date('2026-03-18T10:00:00Z') },
];

const DOCUMENT_STATUS_OPTIONS = Object.keys(STATUS_BADGE_LABELS).filter(s => ![ 'low', 'medium', 'high', 'active', 'completed', 'not_started', 'in_progress'].includes(s)).map(status => ({
  value: status,
  label: STATUS_BADGE_LABELS[status],
}));

const DISCIPLINE_OPTIONS = [
  { value: 'КМ', label: 'Конструкции металлические' },
  { value: 'ЭС', label: 'Электроснабжение' },
  { value: 'ТМ', label: 'Тепломеханика' },
  { value: 'АР', label: 'Архитектурные решения' },
  { value: 'ПС', label: 'Проект силовых сетей' },
  { value: 'ОВ', label: 'Отопление и вентиляция' },
  { value: 'ТХ', label: 'Технологические решения' },
  { value: 'ВК', label: 'Водоснабжение и канализация' },
  { value: '', label: 'Все дисциплины' }, // For resetting filter
];

const ITEMS_PER_PAGE_OPTIONS = [
  { value: 10, label: '10' },
  { value: 25, label: '25' },
  { value: 50, label: '50' },
];

type SortKey = 'code' | 'title' | 'status' | 'created_at';

export default function Documents() {
  const [allDocs, setAllDocs] = useState<Document[]>(MOCK_DOCS);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterDiscipline, setFilterDiscipline] = useState('');
  const [sortBy, setSortBy] = useState<SortKey | null>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(ITEMS_PER_PAGE_OPTIONS[0].value);
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([]);

  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    getDocuments({ search: searchQuery || undefined })
      .then(d => {
        setAllDocs(d);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [searchQuery]);

  const filteredDocs = useMemo(() => {
    let filtered = allDocs;

    if (searchQuery) {
      filtered = filtered.filter(d =>
        d.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (filterStatus) {
      filtered = filtered.filter(d => d.status === filterStatus);
    }

    if (filterDiscipline) {
      filtered = filtered.filter(d => d.discipline === filterDiscipline);
    }

    if (sortBy) {
      filtered = [...filtered].sort((a, b) => {
        const aValue = a[sortBy];
        const bValue = b[sortBy];

        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
        } else if (aValue instanceof Date && bValue instanceof Date) {
            return sortOrder === 'asc' ? aValue.getTime() - bValue.getTime() : bValue.getTime() - aValue.getTime();
        } else if (typeof aValue === 'number' && typeof bValue === 'number') {
            return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
        }
        return 0;
      });
    }
    return filtered;
  }, [allDocs, searchQuery, filterStatus, filterDiscipline, sortBy, sortOrder]);

  const paginatedDocs = useMemo(() => {
    const startIndex = (currentPage - 1) * Number(itemsPerPage);
    const endIndex = startIndex + Number(itemsPerPage);
    return filteredDocs.slice(startIndex, endIndex);
  }, [filteredDocs, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredDocs.length / Number(itemsPerPage));

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(key);
      setSortOrder('asc');
    }
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedDocuments(paginatedDocs.map(doc => doc.id));
    } else {
      setSelectedDocuments([]);
    }
  };

  const handleSelectDocument = (docId: number) => {
    setSelectedDocuments(prev =>
      prev.includes(docId) ? prev.filter(id => id !== docId) : [...prev, docId]
    );
  };

  const isAllSelected = paginatedDocs.length > 0 && selectedDocuments.length === paginatedDocs.length;

  return (
    <div className="space-y-6">
      {/* HEADER AND ACTIONS */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Документы</h1>
          <Button onClick={() => navigate('/documents/new')} size="sm">
            <Plus size={16} className="mr-2" /> Добавить документ
          </Button>
        </div>
      </div>

      {/* FILTERS AND SEARCH */}
      <Card className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Input
            label="Поиск"
            placeholder="Код или название..."
            icon={Search}
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="col-span-full lg:col-span-1"
          />
          <Select
            label="Статус"
            options={[{ value: '', label: 'Все статусы' }, ...DOCUMENT_STATUS_OPTIONS]}
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value)}
          />
          <Select
            label="Дисциплина"
            options={DISCIPLINE_OPTIONS}
            value={filterDiscipline}
            onChange={e => setFilterDiscipline(e.target.value)}
          />
          <div className="flex items-end justify-end">
            <Button 
              variant="secondary" 
              onClick={() => {
                setSearchQuery('');
                setFilterStatus('');
                setFilterDiscipline('');
                setSortBy('created_at');
                setSortOrder('desc');
                setCurrentPage(1);
              }}
            >
              Сбросить фильтры
            </Button>
          </div>
        </div>
      </Card>

      {/* DOCUMENTS TABLE */}
      <Card padding="none" className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left w-12">
                  <input
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 shadow-sm focus:ring-primary-500"
                    onChange={handleSelectAll}
                    checked={isAllSelected}
                  />
                </th>
                <TableHeader sortKey="code" currentSortBy={sortBy} currentSortOrder={sortOrder} onSort={handleSort}>Код</TableHeader>
                <TableHeader sortKey="title" currentSortBy={sortBy} currentSortOrder={sortOrder} onSort={handleSort}>Название</TableHeader>
                <TableHeader sortKey="doc_type" currentSortBy={sortBy} currentSortOrder={sortOrder} onSort={handleSort}>Тип</TableHeader>
                <TableHeader sortKey="discipline" currentSortBy={sortBy} currentSortOrder={sortOrder} onSort={handleSort}>Дисциплина</TableHeader>
                <TableHeader sortKey="status" currentSortBy={sortBy} currentSortOrder={sortOrder} onSort={handleSort}>Статус</TableHeader>
                <TableHeader sortKey="created_at" currentSortBy={sortBy} currentSortOrder={sortOrder} onSort={handleSort}>Создан</TableHeader>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                Array.from({ length: Number(itemsPerPage) }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 w-4 bg-gray-100 rounded" /></td>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 bg-gray-100 rounded w-24" /></td>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 bg-gray-100 rounded w-48" /></td>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 bg-gray-100 rounded w-16" /></td>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 bg-gray-100 rounded w-20" /></td>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 bg-gray-100 rounded w-20" /></td>
                    <td className="px-6 py-4 whitespace-nowrap"><div className="h-4 bg-gray-100 rounded w-24" /></td>
                  </tr>
                ))
              ) : paginatedDocs.length > 0 ? (
                paginatedDocs.map(d => (
                  <tr key={d.id} className="group hover:bg-gray-50 transition-colors cursor-pointer">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        className="rounded border-gray-300 text-primary-600 shadow-sm focus:ring-primary-500"
                        checked={selectedDocuments.includes(d.id)}
                        onChange={() => handleSelectDocument(d.id)}
                        onClick={(e) => e.stopPropagation()} // Prevent row click from triggering
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 group-hover:text-primary-700" onClick={() => navigate(`/documents/${d.id}`)}>{d.code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700" onClick={() => navigate(`/documents/${d.id}`)}>{d.title}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" onClick={() => navigate(`/documents/${d.id}`)}>{d.doc_type || '—'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" onClick={() => navigate(`/documents/${d.id}`)}>{d.discipline || '—'}</td>
                    <td className="px-6 py-4 whitespace-nowrap" onClick={() => navigate(`/documents/${d.id}`)}><Badge variant={mapStatusToBadgeVariant(d.status)}>{mapStatusToBadgeLabel(d.status)}</Badge></td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500" onClick={() => navigate(`/documents/${d.id}`)}>{d.created_at ? new Date(d.created_at).toLocaleDateString() : '—'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-400">
                    <div className="flex flex-col items-center gap-2">
                      <Info size={32} strokeWidth={1} />
                      <p>Документы не найдены</p>
                      <p className="text-sm">Попробуйте изменить фильтры или добавить новый документ.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* PAGINATION */}
        {filteredDocs.length > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <Button onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))} disabled={currentPage === 1} variant="outline" size="sm">Предыдущая</Button>
              <Button onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))} disabled={currentPage === totalPages} variant="outline" size="sm">Следующая</Button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Показано <span className="font-medium">{(currentPage - 1) * Number(itemsPerPage) + 1}</span> по <span className="font-medium">{Math.min(currentPage * Number(itemsPerPage), filteredDocs.length)}</span> из <span className="font-medium">{filteredDocs.length}</span> документов.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Select
                  options={ITEMS_PER_PAGE_OPTIONS}
                  value={itemsPerPage}
                  onChange={e => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1); // Reset to first page when items per page changes
                  }}
                  className="w-24"
                  label=""
                />
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-l-md"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft size={16} />
                  </Button>
                  {[...Array(totalPages)].map((_, i) => (
                    <Button
                      key={i + 1}
                      variant={currentPage === i + 1 ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setCurrentPage(i + 1)}
                      className={`${currentPage === i + 1 ? 'z-10 bg-primary-50 border-primary-500 text-primary-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}
                        ${i + 1 === 1 ? 'rounded-l-md' : ''} ${i + 1 === totalPages ? 'rounded-r-md' : ''} 
                        relative inline-flex items-center px-4 py-2 border text-sm font-medium focus:z-10 `}
                    >
                      {i + 1}
                    </Button>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-r-md"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <ChevronRight size={16} />
                  </Button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* BULK ACTIONS BAR */}
      {selectedDocuments.length > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white p-4 rounded-lg shadow-xl flex items-center gap-4 animate-in slide-in-from-bottom duration-300 z-50">
          <p className="text-sm font-medium">Выбрано: {selectedDocuments.length}</p>
          <Button variant="secondary" size="sm" className="bg-gray-700 text-white hover:bg-gray-600">Изменить статус</Button>
          <Button variant="danger" size="sm">Удалить</Button>
        </div>
      )}
    </div>
  );
}

interface TableHeaderProps {
  children: React.ReactNode;
  sortKey: SortKey;
  currentSortBy: SortKey | null;
  currentSortOrder: 'asc' | 'desc';
  onSort: (key: SortKey) => void;
}

function TableHeader({ children, sortKey, currentSortBy, currentSortOrder, onSort }: TableHeaderProps) {
  const isSorted = currentSortBy === sortKey;
  const isAsc = isSorted && currentSortOrder === 'asc';
  const isDesc = isSorted && currentSortOrder === 'desc';

  return (
    <th 
      className="px-6 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider cursor-pointer select-none hover:text-gray-600 transition-colors"
      onClick={() => onSort(sortKey)}
    >
      <div className="flex items-center gap-1.5">
        {children}
        <span className="flex flex-col">
          <ChevronUp size={12} className={`${isAsc ? 'text-gray-900' : 'text-gray-300'}`} />
          <ChevronDown size={12} className={`${isDesc ? 'text-gray-900' : 'text-gray-300'} -mt-1`} />
        </span>
      </div>
    </th>
  );
}
