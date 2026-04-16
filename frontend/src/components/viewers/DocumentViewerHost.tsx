import { useMemo } from 'react';
import { PDFViewer } from './PDFViewer';
import { ImageViewer } from './ImageViewer';
import { ExcelViewer } from './ExcelViewer';
import { WordViewer } from './WordViewer';
import { DWGViewer } from './DWGViewer';
import { FileIcon } from './FileIcon';
import { useWorkspaceStore } from '../workspace/store/workspaceStore';

/**
 * DocumentViewerHost - единый host компонент для отображения документов разных типов
 * Определяет тип файла и рендерит соответствующий viewer
 */
export default function DocumentViewerHost() {
  const { activeTabId, openTabs } = useWorkspaceStore();
  const activeTab = openTabs.find((t) => t.id === activeTabId);

  // Получаем файл из tab (предполагаем что файл может быть сохранён в tab metadata)
  const file = activeTab?.file as FileWithMeta | null;

  // Определяем тип файла
  const fileType = useMemo(() => {
    if (!file) return null;
    return detectFileType(file);
  }, [file]);

  // Если файл не выбран - показываем пустое состояние
  if (!activeTab || !file) {
    return <EmptyState />;
  }

  // Рендер соответствующего viewer
  switch (fileType) {
    case 'pdf':
      return <PDFViewer file={file} />;
    case 'image':
      return <ImageViewer file={file} />;
    case 'excel':
      return <ExcelViewer file={file} />;
    case 'word':
      return <WordViewer file={file} />;
    case 'dwg':
      return <DWGViewer file={file} />;
    case 'csv':
      return <CSVViewer file={file} />;
    default:
      return <UnsupportedFileType file={file} fileType={fileType} />;
  }
}

interface FileWithMeta extends File {
  url?: string;
  previewUrl?: string;
  metadata?: Record<string, any>;
}

function detectFileType(file: File): FileType {
  const extension = file.name.split('.').pop()?.toLowerCase() || '';
  const mimeType = file.type;

  // PDF
  if (mimeType === 'application/pdf' || extension === 'pdf') {
    return 'pdf';
  }

  // Изображения
  if (
    mimeType.startsWith('image/') ||
    ['png', 'jpg', 'jpeg', 'webp', 'svg', 'tiff', 'gif'].includes(extension)
  ) {
    return 'image';
  }

  // Excel
  if (
    mimeType.includes('excel') ||
    mimeType.includes('spreadsheet') ||
    ['xls', 'xlsx', 'xlsm'].includes(extension)
  ) {
    return 'excel';
  }

  // Word
  if (
    mimeType.includes('word') ||
    ['doc', 'docx'].includes(extension)
  ) {
    return 'word';
  }

  // DWG
  if (extension === 'dwg' || extension === 'dxf') {
    return 'dwg';
  }

  // CSV
  if (extension === 'csv' || mimeType === 'text/csv') {
    return 'csv';
  }

  return 'unknown';
}

type FileType = 'pdf' | 'image' | 'excel' | 'word' | 'dwg' | 'csv' | 'unknown';

// Пустое состояние
function EmptyState() {
  return (
    <div
      className="flex-1 flex items-center justify-center"
      style={{ backgroundColor: 'var(--bg-app)' }}
    >
      <div className="text-center max-w-md px-6">
        <div
          className="mx-auto w-14 h-14 rounded-xl flex items-center justify-center mb-4"
          style={{ backgroundColor: 'var(--bg-surface-2)' }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style={{ color: 'var(--text-tertiary)' }}>
            <path
              d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <polyline points="14 2 14 8 20 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="10 9 9 9 8 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <h3
          className="text-base font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Выберите документ из Explorer
        </h3>
        <p
          className="text-sm"
          style={{ color: 'var(--text-secondary)' }}
        >
          Документ откроется в этом окне для просмотра
        </p>
      </div>
    </div>
  );
}

// Неподдерживаемый тип файла
interface UnsupportedFileTypeProps {
  file: File;
  fileType: string | null;
}

function UnsupportedFileType({ file }: UnsupportedFileTypeProps) {
  return (
    <div
      className="flex-1 flex items-center justify-center"
      style={{ backgroundColor: 'var(--bg-app)' }}
    >
      <div className="text-center max-w-md px-6">
        <div
          className="mx-auto w-14 h-14 rounded-xl flex items-center justify-center mb-4"
          style={{ backgroundColor: 'var(--bg-surface-2)' }}
        >
          <FileIcon fileName={file.name} />
        </div>
        <h3
          className="text-base font-semibold mb-2"
          style={{ color: 'var(--text-primary)' }}
        >
          Формат не поддерживается
        </h3>
        <p
          className="text-sm mb-4"
          style={{ color: 'var(--text-secondary)' }}
        >
          Просмотр файлов этого типа пока недоступен.
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

// CSV Viewer (упрощённая версия Excel)
function CSVViewer({ file }: { file: File }) {
  return (
    <div
      className="flex-1 overflow-hidden flex flex-col"
      style={{ backgroundColor: 'var(--bg-app)' }}
    >
      <div
        className="px-4 py-2 border-b flex items-center justify-between"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-default)' }}
      >
        <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
          CSV файл: {file.name}
        </h3>
        <a
          href={URL.createObjectURL(file)}
          download={file.name}
          className="text-xs px-2 py-1 rounded transition-colors"
          style={{
            backgroundColor: 'var(--accent-engineering)',
            color: 'var(--text-inverse)',
          }}
        >
          Скачать
        </a>
      </div>
      <div
        className="flex-1 overflow-auto p-4"
        style={{ backgroundColor: 'var(--bg-surface-2)' }}
      >
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Для просмотра CSV файлов используйте Excel или аналогичное приложение.
        </p>
      </div>
    </div>
  );
}
