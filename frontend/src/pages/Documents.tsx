import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDocuments } from '../api/documents';
import type { Document } from '../types';
import StatusBadge from '../components/StatusBadge';
import { Search, FileText } from 'lucide-react';

const MOCK_DOCS: Document[] = [
  { id: 1, code: 'НПЗ-КМ-001', title: 'Общий вид конструкций', project_id: 1, status: 'approved', doc_type: 'КМ', current_revision_id: 3 },
  { id: 2, code: 'НПЗ-КМ-002', title: 'Узлы сопряжения', project_id: 1, status: 'on_review', doc_type: 'КМ', current_revision_id: 5 },
  { id: 3, code: 'ЛЭП-ЭС-001', title: 'Схема электроснабжения', project_id: 2, status: 'draft', doc_type: 'ЭС', current_revision_id: null },
  { id: 4, code: 'КОТ-ТМ-001', title: 'Тепломеханические решения', project_id: 3, status: 'in_progress', doc_type: 'ТМ', current_revision_id: 2 },
];

export default function Documents() {
  const [docs, setDocs] = useState<Document[]>(MOCK_DOCS);
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    getDocuments({ search: search || undefined }).then(setDocs).catch(() => {});
  }, [search]);

  const filtered = docs.filter(d =>
    !search || d.code.toLowerCase().includes(search.toLowerCase()) || d.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Документы</h1>
        <div className="relative">
          <Search size={18} className="absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text" placeholder="Поиск по коду или названию..."
            value={search} onChange={e => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 border rounded-lg w-72 focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Код</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Название</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Тип</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Статус</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map(d => (
              <tr key={d.id} onClick={() => navigate(`/documents/${d.id}`)} className="hover:bg-gray-50 cursor-pointer">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-gray-400" />
                    <span className="font-medium">{d.code}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">{d.title}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{d.doc_type}</td>
                <td className="px-6 py-4"><StatusBadge status={d.status} /></td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={4} className="px-6 py-12 text-center text-gray-400">Документы не найдены</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
