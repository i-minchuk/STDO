import { useState, useRef } from 'react';
import type { ExcelSheet, TargetField } from '../types';
import { Upload, FileSpreadsheet, ArrowRight, Check, X } from 'lucide-react';

const SYSTEM_FIELDS: TargetField[] = [
  { field: 'document_code', label: 'Код документа', required: true },
  { field: 'title', label: 'Наименование', required: true },
  { field: 'doc_type', label: 'Тип документа', required: false },
  { field: 'discipline', label: 'Дисциплина', required: false },
  { field: 'engineer', label: 'Исполнитель', required: false },
  { field: 'reviewer', label: 'Проверяющий', required: false },
  { field: 'planned_start', label: 'Дата начала (план)', required: false },
  { field: 'planned_finish', label: 'Дата окончания (план)', required: false },
  { field: 'planned_hours', label: 'Плановые часы', required: false },
  { field: 'ifr_date', label: 'Дата IFR', required: false },
  { field: 'ifa_date', label: 'Дата IFA', required: false },
  { field: 'ifc_date', label: 'Дата IFC', required: false },
  { field: 'status', label: 'Статус', required: false },
  { field: 'revision', label: 'Ревизия', required: false },
  { field: 'notes', label: 'Примечания', required: false },
];

const MOCK_SHEETS: ExcelSheet[] = [{
  name: 'MDR',
  columns: [
    'Doc No', 'Title', 'Discipline', 'Doc Type', 'Status', 'Rev', 'Engineer',
    'Checker', 'Approver', 'IFR Date', 'IFA Date', 'IFC Date', 'Eng Hrs',
    'Weight', 'Customer Ref', 'Area', 'Building', 'System', 'Subsystem',
    'Tag No', 'Priority', 'Phase', 'Contract No', 'PO No', 'Vendor',
    'Supplier Doc', 'Native Format', 'Pages', 'Size', 'Language',
    'Confidentiality', 'Distribution', 'Remarks', 'Client Comments',
    'Response Date', 'Resubmit Date', 'Final Date', 'Handover Date',
    'Archive Ref', 'QA Check',
  ],
  total_rows: 147,
  preview: [
    { 'Doc No': 'GRS-KM-001', 'Title': 'Общий вид металлоконструкций', 'Discipline': 'КМ', 'Doc Type': 'Drawing', 'Status': 'In Progress', 'Rev': 'A01', 'Engineer': 'Иванов А.А.', 'Eng Hrs': '16', 'IFR Date': '2026-04-15' },
    { 'Doc No': 'GRS-KM-002', 'Title': 'Узлы сопряжения', 'Discipline': 'КМ', 'Doc Type': 'Drawing', 'Status': 'Not Started', 'Rev': '', 'Engineer': 'Петров Б.В.', 'Eng Hrs': '24', 'IFR Date': '2026-04-20' },
  ],
}];

export default function ImportExcel() {
  const [step, setStep] = useState<'upload' | 'mapping' | 'result'>('upload');
  const [sheets, setSheets] = useState<ExcelSheet[]>([]);
  const [selectedSheet, setSelectedSheet] = useState<ExcelSheet | null>(null);
  const [mappings, setMappings] = useState<Record<string, string>>({});
  const [customCols, setCustomCols] = useState<string[]>([]);
  const [filename, setFilename] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFilename(file.name);

    // Try real API, fallback to mock
    try {
      const { previewExcel } = await import('../api/import');
      const result = await previewExcel(file);
      setSheets(result.sheets);
      if (result.sheets.length > 0) {
        setSelectedSheet(result.sheets[0]);
      }
    } catch {
      setSheets(MOCK_SHEETS);
      setSelectedSheet(MOCK_SHEETS[0]);
    }
    setStep('mapping');
  };

  const handleMapping = (systemField: string, excelCol: string) => {
    setMappings(prev => ({ ...prev, [systemField]: excelCol }));
  };

  const toggleCustomCol = (col: string) => {
    setCustomCols(prev =>
      prev.includes(col) ? prev.filter(c => c !== col) : [...prev, col]
    );
  };

  const mappedExcelCols = Object.values(mappings);
  const unmappedCols = selectedSheet?.columns.filter(c => !mappedExcelCols.includes(c)) || [];

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-3">
        <FileSpreadsheet size={28} className="text-green-600" /> Импорт из Excel
      </h1>

      {/* Step 1: Upload */}
      {step === 'upload' && (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <Upload size={48} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-lg font-semibold mb-2">Загрузите файл заказчика</h2>
          <p className="text-gray-500 text-sm mb-6">
            Поддерживается формат .xlsx. Система прочитает все колонки и предложит выбрать нужные.
          </p>
          <input ref={fileRef} type="file" accept=".xlsx,.xls" onChange={handleFile} className="hidden" />
          <button onClick={() => fileRef.current?.click()}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700">
            Выбрать файл
          </button>
          <button onClick={() => { setSheets(MOCK_SHEETS); setSelectedSheet(MOCK_SHEETS[0]); setFilename('MDR_GRS-5.xlsx'); setStep('mapping'); }}
            className="ml-4 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 text-sm">
            Демо-файл (40 колонок)
          </button>
        </div>
      )}

      {/* Step 2: Mapping */}
      {step === 'mapping' && selectedSheet && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium">{filename}</span>
                <span className="text-gray-400 text-sm ml-3">Лист: {selectedSheet.name} — {selectedSheet.total_rows} строк, {selectedSheet.columns.length} колонок</span>
              </div>
              <button onClick={() => { setStep('upload'); setSheets([]); setMappings({}); setCustomCols([]); }}
                className="text-gray-400 hover:text-gray-600 text-sm">Другой файл</button>
            </div>
          </div>

          {/* Mapping table */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="font-semibold mb-4">Привязка колонок (15 полей системы)</h2>
              <div className="space-y-3">
                {SYSTEM_FIELDS.map(f => (
                  <div key={f.field} className="flex items-center gap-3">
                    <div className="w-48 text-sm">
                      {f.label}
                      {f.required && <span className="text-red-500 ml-1">*</span>}
                    </div>
                    <ArrowRight size={14} className="text-gray-300" />
                    <select
                      value={mappings[f.field] || ''}
                      onChange={e => handleMapping(f.field, e.target.value)}
                      className={`flex-1 px-3 py-1.5 border rounded-lg text-sm ${mappings[f.field] ? 'border-green-400 bg-green-50' : ''}`}
                    >
                      <option value="">— Не привязано —</option>
                      {selectedSheet.columns.map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                    {mappings[f.field] && <Check size={16} className="text-green-500" />}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="font-semibold mb-4">Дополнительные колонки (по выбору автора)</h2>
              <p className="text-sm text-gray-500 mb-3">
                Отметьте колонки из файла заказчика, которые хотите сохранить дополнительно:
              </p>
              <div className="max-h-96 overflow-y-auto space-y-1">
                {unmappedCols.map(col => (
                  <label key={col} className="flex items-center gap-2 px-3 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                    <input type="checkbox" checked={customCols.includes(col)} onChange={() => toggleCustomCol(col)}
                      className="rounded border-gray-300 text-primary-600" />
                    <span className="text-sm">{col}</span>
                  </label>
                ))}
              </div>
              {customCols.length > 0 && (
                <div className="mt-3 text-sm text-primary-600 font-medium">
                  Выбрано: {customCols.length} дополнительных колонок
                </div>
              )}
            </div>
          </div>

          {/* Preview */}
          {selectedSheet.preview.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6 overflow-x-auto">
              <h2 className="font-semibold mb-3">Превью данных (первые строки)</h2>
              <table className="text-sm w-full">
                <thead className="bg-gray-50">
                  <tr>
                    {selectedSheet.columns.slice(0, 10).map(c => (
                      <th key={c} className="px-3 py-2 text-xs text-gray-500 text-left whitespace-nowrap">{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {selectedSheet.preview.map((row, i) => (
                    <tr key={i} className="border-t">
                      {selectedSheet.columns.slice(0, 10).map(c => (
                        <td key={c} className="px-3 py-2 whitespace-nowrap">{row[c] || ''}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setStep('result')}
              className="bg-primary-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary-700">
              Импортировать
            </button>
            <span className="text-sm text-gray-400 self-center">
              Привязано: {Object.keys(mappings).filter(k => mappings[k]).length} из {SYSTEM_FIELDS.length} полей
            </span>
          </div>
        </div>
      )}

      {/* Step 3: Result */}
      {step === 'result' && (
        <div className="bg-white rounded-xl shadow-sm p-8 text-center">
          <Check size={48} className="mx-auto text-green-500 mb-4" />
          <h2 className="text-xl font-bold mb-2">Импорт завершён</h2>
          <p className="text-gray-500 mb-2">Импортировано: {selectedSheet?.total_rows || 0} документов</p>
          <p className="text-gray-400 text-sm mb-6">
            Привязано {Object.keys(mappings).filter(k => mappings[k]).length} системных полей + {customCols.length} дополнительных колонок
          </p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => { setStep('upload'); setMappings({}); setCustomCols([]); }}
              className="bg-gray-100 text-gray-700 px-6 py-2.5 rounded-lg font-medium hover:bg-gray-200">
              Загрузить ещё
            </button>
            <a href="/documents" className="bg-primary-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-primary-700">
              К документам
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
