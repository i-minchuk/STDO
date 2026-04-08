import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getDocument } from '../api/documents';
import type { DocumentDetail as DocDetail } from '../types';
import { FileText, Download, Info, GitFork, ListTodo, History, Plus } from 'lucide-react';
import { Badge, Button, Card, Tabs } from '../components/ui';
import { useAuth } from '../context/AuthContext'; // Assume this is available for created_by/approved_by mapping
import { mapStatusToBadgeVariant, mapStatusToBadgeLabel } from '../utils/status-mappers';

const MOCK_DOC: DocDetail = {
  id: 1, code: 'НПЗ-КМ-001', title: 'Общий вид конструкций', project_id: 1,
  status: 'approved', doc_type: 'КМ', current_revision_id: 3, discipline: 'КМ',
  created_by: 1, created_at: new Date('2026-01-15T10:00:00Z'),
  revisions: [
    { id: 1, document_id: 1, revision_index: 'A.1', revision_letter: 'A', revision_number: 1, version_number: 1, status: 'superseded', file_path: '/files/rev1.pdf', change_log: 'Первая версия', created_by: 1, created_at: new Date('2026-01-20T10:00:00Z'), approved_by: 2, approved_at: new Date('2026-01-25T10:00:00Z') },
    { id: 2, document_id: 1, revision_index: 'A.2', revision_letter: 'A', revision_number: 2, version_number: 2, status: 'superseded', file_path: '/files/rev2.pdf', change_log: 'Незначительные правки', created_by: 1, created_at: new Date('2026-02-10T10:00:00Z'), approved_by: 2, approved_at: new Date('2026-02-15T10:00:00Z') },
    { id: 3, document_id: 1, revision_index: 'B.1', revision_letter: 'B', revision_number: 1, version_number: 3, status: 'approved', file_path: '/files/rev3.pdf', change_log: 'Изменения по замечаниям экспертизы', created_by: 1, created_at: new Date('2026-03-05T10:00:00Z'), approved_by: 2, approved_at: new Date('2026-03-10T10:00:00Z') },
  ],
};

export default function DocumentDetailPage() {
  const { id } = useParams();
  const [doc, setDoc] = useState<DocDetail | null>(null);
  const { user } = useAuth(); // Access user context

  useEffect(() => {
    if (id) getDocument(Number(id)).then(setDoc).catch(() => {});
  }, [id]);

  if (!doc) {
    return (
      <Card className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded mb-4 w-3/4"></div>
        <div className="h-4 bg-gray-200 rounded mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        <div className="h-48 mt-6 bg-gray-200 rounded"></div>
      </Card>
    );
  }

  const tabs = [
    {
      label: 'Обзор',
      icon: Info,
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-500 font-medium">Наименование</p>
              <p className="text-gray-900 font-medium">{doc.title}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 font-medium">Дисциплина</p>
              <p className="text-gray-900 font-medium">{doc.discipline || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 font-medium">Создан</p>
              <p className="text-gray-900 font-medium">
                {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : '—'} {doc.created_by && `(ID: ${doc.created_by})`}
              </p>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-500 font-medium">Текущий статус</p>
              <Badge variant={mapStatusToBadgeVariant(doc.status)}>{mapStatusToBadgeLabel(doc.status)}</Badge>
            </div>
            <div>
              <p className="text-xs text-gray-500 font-medium">Текущая ревизия</p>
              <p className="text-gray-900 font-medium">{doc.revisions.find(r => r.id === doc.current_revision_id)?.revision_index || '—'}</p>
            </div>
          </div>
        </div>
      ),
    },
    {
      label: 'Ревизии',
      icon: GitFork,
      content: (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Версия</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Индекс</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Создана</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Утверждена</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Описание изменений</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Действия</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {doc.revisions.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{r.revision_letter}.{r.revision_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{r.revision_index} ({r.version_number})</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge variant={mapStatusToBadgeVariant(r.status)}>{mapStatusToBadgeLabel(r.status)}</Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {r.created_at ? new Date(r.created_at).toLocaleDateString() : '—'}
                    {r.created_by && <span className="block text-xs text-gray-400">ID: {r.created_by}</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {r.approved_at ? new Date(r.approved_at).toLocaleDateString() : '—'}
                    {r.approved_by && <span className="block text-xs text-gray-400">ID: {r.approved_by}</span>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{r.change_log || '—'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {r.file_path ? (
                      <Button variant="ghost" size="sm" className="text-primary-600 hover:text-primary-700 flex items-center gap-1">
                        <Download size={14} /> Скачать
                      </Button>
                    ) : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ),
    },
    {
      label: 'Задачи',
      icon: ListTodo,
      content: (
        <div className="py-12 text-center text-gray-400 flex flex-col items-center gap-2">
          <ListTodo size={32} strokeWidth={1} />
          <p>Нет связанных задач</p>
          <Button variant="ghost" size="sm"><Plus size={16} className="mr-1"/> Добавить задачу</Button>
        </div>
      ),
    },
    {
      label: 'Журнал изменений',
      icon: History,
      content: (
        <div className="py-12 text-center text-gray-400 flex flex-col items-center gap-2">
          <History size={32} strokeWidth={1} />
          <p>Журнал изменений пуст</p>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* DOCUMENT HEADER & ACTIONS */}
      <Card className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <FileText size={24} className="text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">{doc.code}</h1>
            <Badge variant={mapStatusToBadgeVariant(doc.status)}>{mapStatusToBadgeLabel(doc.status)}</Badge>
          </div>
          <p className="text-gray-600 text-lg">{doc.title}</p>
        </div>
        <div className="flex flex-col gap-2">
          <Button><Plus size={16} className="mr-2" /> Создать ревизию</Button>
          {doc.revisions.find(r => r.id === doc.current_revision_id)?.file_path && (
             <Button variant="outline"><Download size={16} className="mr-2" /> Скачать текущую</Button>
          )}
        </div>
      </Card>

      {/* DOCUMENT TABS */}
      <Card padding="none">
        <Tabs tabs={tabs} />
      </Card>
    </div>
  );
}
