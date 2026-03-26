import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getDocument } from '../api/documents';
import type { DocumentDetail as DocDetail } from '../types';
import StatusBadge from '../components/StatusBadge';
import { FileText, Download } from 'lucide-react';

const MOCK_DOC: DocDetail = {
  id: 1, code: 'НПЗ-КМ-001', title: 'Общий вид конструкций', project_id: 1,
  status: 'approved', doc_type: 'КМ', current_revision_id: 3,
  revisions: [
    { id: 1, letter: 'A', number: 1, status: 'superseded', created_at: '2026-01-20', file_path: '/files/rev1.pdf' },
    { id: 2, letter: 'A', number: 2, status: 'superseded', created_at: '2026-02-10', file_path: '/files/rev2.pdf' },
    { id: 3, letter: 'B', number: 1, status: 'approved', created_at: '2026-03-05', file_path: '/files/rev3.pdf' },
  ],
};

export default function DocumentDetailPage() {
  const { id } = useParams();
  const [doc, setDoc] = useState<DocDetail>(MOCK_DOC);

  useEffect(() => {
    if (id) getDocument(Number(id)).then(setDoc).catch(() => {});
  }, [id]);

  return (
    <div>
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <FileText size={24} className="text-primary-600" />
              <h1 className="text-2xl font-bold">{doc.code}</h1>
              <StatusBadge status={doc.status} />
            </div>
            <p className="text-gray-600">{doc.title}</p>
            <p className="text-sm text-gray-400 mt-1">Тип: {doc.doc_type}</p>
          </div>
          <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 text-sm font-medium">
            Создать ревизию
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b bg-gray-50">
          <h2 className="font-semibold">История ревизий</h2>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Версия</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Статус</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Дата</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Файл</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {doc.revisions.map(r => (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium">{r.letter}.{r.number}</td>
                <td className="px-6 py-4"><StatusBadge status={r.status} /></td>
                <td className="px-6 py-4 text-sm text-gray-600">{r.created_at || '—'}</td>
                <td className="px-6 py-4">
                  {r.file_path ? (
                    <button className="text-primary-600 hover:text-primary-700 flex items-center gap-1 text-sm">
                      <Download size={14} /> Скачать
                    </button>
                  ) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
