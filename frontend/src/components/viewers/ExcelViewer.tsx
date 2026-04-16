import { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';

interface ExcelViewerProps {
  file: File;
}

interface SheetData {
  name: string;
  headers: string[];
  rows: string[][];
}

export function ExcelViewer({ file }: ExcelViewerProps) {
  const [sheets, setSheets] = useState<SheetData[]>([]);
  const [activeSheetIndex, setActiveSheetIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadExcelFile = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const arrayBuffer = await file.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });

        const sheetData: SheetData[] = workbook.SheetNames.map((sheetName) => {
          const worksheet = workbook.Sheets[sheetName];
          const json = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

          if (json.length === 0) {
            return {
              name: sheetName,
              headers: [],
              rows: [],
            };
          }

          const headers = json[0] as string[];
          const rows = json.slice(1) as string[][];

          return {
            name: sheetName,
            headers,
            rows,
          };
        });

        setSheets(sheetData);

        if (sheetData.length > 0) {
          setActiveSheetIndex(0);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Не удалось загрузить файл');
      } finally {
        setIsLoading(false);
      }
    };

    loadExcelFile();
  }, [file]);

  const activeSheet = sheets[activeSheetIndex];

  if (error) {
    return (
      <div
        className="flex-1 flex items-center justify-center"
        style={{ backgroundColor: 'var(--bg-app)' }}
      >
        <div className="text-center">
          <p className="text-sm mb-2" style={{ color: 'var(--error)' }}>
            Ошибка загрузки Excel: {error}
          </p>
          <a
            href={URL.createObjectURL(file)}
            download={file.name}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{
              backgroundColor: 'var(--accent-engineering)',
              color: 'var(--text-inverse)',
            }}
          >
            Скачать файл
          </a>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        className="flex-1 flex items-center justify-center"
        style={{ backgroundColor: 'var(--bg-app)' }}
      >
        <div className="text-center">
          <div
            className="w-8 h-8 border-2 border-t-2 rounded-full animate-spin mx-auto mb-2"
            style={{ borderColor: 'var(--border-default)', borderTopColor: 'var(--accent-engineering)' }}
          />
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Загрузка Excel...
          </p>
        </div>
      </div>
    );
  }

  if (!activeSheet) {
    return (
      <div
        className="flex-1 flex items-center justify-center"
        style={{ backgroundColor: 'var(--bg-app)' }}
      >
        <div className="text-center">
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Нет данных для отображения
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex-1 flex flex-col overflow-hidden"
      style={{ backgroundColor: 'var(--bg-app)' }}
    >
      {/* Toolbar */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b shrink-0"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-default)' }}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
            {file.name}
          </span>
        </div>

        {/* Sheet Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto">
          {sheets.map((sheet, index) => (
            <button
              key={sheet.name}
              onClick={() => setActiveSheetIndex(index)}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors whitespace-nowrap ${
                index === activeSheetIndex
                  ? ''
                  : 'opacity-60 hover:opacity-100'
              }`}
              style={{
                backgroundColor: index === activeSheetIndex ? 'var(--bg-surface-2)' : 'transparent',
                color: index === activeSheetIndex ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              {sheet.name}
            </button>
          ))}
        </div>

        <a
          href={URL.createObjectURL(file)}
          download={file.name}
          className="p-1.5 rounded transition-colors"
          style={{ color: 'var(--text-secondary)' }}
          title="Скачать"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
        </a>
      </div>

      {/* Spreadsheet */}
      <div
        className="flex-1 overflow-auto"
        style={{ backgroundColor: 'var(--bg-surface-2)' }}
      >
        <table
          className="w-full border-collapse"
          style={{ minWidth: '100%' }}
        >
          <thead>
            <tr style={{ backgroundColor: 'var(--bg-surface)' }}>
              <th
                className="border-r border-b px-2 py-1.5 text-xs font-semibold text-center"
                style={{ 
                  borderColor: 'var(--border-default)',
                  color: 'var(--text-tertiary)',
                  width: '40px',
                }}
              >
                #
              </th>
              {activeSheet.headers.map((header, index) => (
                <th
                  key={index}
                  className="border-r border-b px-2 py-1.5 text-xs font-semibold text-left min-w-[100px]"
                  style={{ 
                    borderColor: 'var(--border-default)',
                    color: 'var(--text-primary)',
                  }}
                >
                  {String(header || `Col ${index + 1}`)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {activeSheet.rows.length === 0 ? (
              <tr>
                <td
                  className="px-2 py-4 text-center"
                  colSpan={activeSheet.headers.length + 1}
                  style={{ color: 'var(--text-tertiary)' }}
                >
                  Нет данных
                </td>
              </tr>
            ) : (
              activeSheet.rows.map((row, rowIndex) => (
                <tr key={rowIndex} style={{ backgroundColor: rowIndex % 2 === 0 ? 'transparent' : 'var(--bg-hover)' }}>
                  <td
                    className="border-r border-b px-2 py-1.5 text-xs text-center"
                    style={{ 
                      borderColor: 'var(--border-default)',
                      color: 'var(--text-tertiary)',
                    }}
                  >
                    {rowIndex + 1}
                  </td>
                  {activeSheet.headers.map((_, colIndex) => (
                    <td
                      key={colIndex}
                      className="border-r border-b px-2 py-1.5 text-xs"
                      style={{ 
                        borderColor: 'var(--border-default)',
                        color: 'var(--text-primary)',
                      }}
                    >
                      {String(row[colIndex] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div
        className="px-4 py-1.5 border-t text-xs text-center shrink-0"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-default)' }}
      >
        <span style={{ color: 'var(--text-tertiary)' }}>
          {file.name} · {activeSheet.name} · {activeSheet.rows.length} строк(и)
        </span>
      </div>
    </div>
  );
}
