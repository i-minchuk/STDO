import { useState, useEffect, useCallback } from 'react';

interface WordViewerProps {
  file: File;
}

/**
 * WordViewer - просмотрщик для .doc и .docx файлов
 * 
 * Для локального рендеринга Word документов в браузере требуется:
 * 1. mammoth.js (для конвертации docx в HTML) - лёгкий, но только базовое форматирование
 * 2. Office Online Viewer (через iframe) - требует интернет
 * 3. Microsoft 365 API - требует аутентификацию
 * 
 * Реализован fallback strategy с поддержкой mammoth.js для базового просмотра
 */
export function WordViewer({ file }: WordViewerProps) {
  const [content, setContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useFallback, setUseFallback] = useState(false);

  const fileUrl = URL.createObjectURL(file);

  const loadDocument = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const extension = file.name.split('.').pop()?.toLowerCase();

    // Для .docx используем mammoth.js если доступен
    if (extension === 'docx' && !useFallback) {
      try {
        // Проверка availability mammoth
        const mammoth = await import('mammoth');
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.convertToHtml({ arrayBuffer });
        
        setContent(result.value);
      } catch (err) {
        // Если mammoth не доступен или ошибка - переходим к fallback
        if ((err as Error).message.includes('Cannot find module')) {
          setUseFallback(true);
        } else {
          setError('Не удалось загрузить документ. Попробуйте скачать файл.');
        }
      }
    } else {
      // Для .doc или fallback
      setUseFallback(true);
    }

    setIsLoading(false);
  }, [file, useFallback]);

  useEffect(() => {
    loadDocument();
  }, [loadDocument]);

  const fileExtension = file.name.split('.').pop()?.toLowerCase();

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
            Загрузка Word-документа...
          </p>
        </div>
      </div>
    );
  }

  if (useFallback || error) {
    return (
      <div
        className="flex-1 flex flex-col items-center justify-center"
        style={{ backgroundColor: 'var(--bg-app)' }}
      >
        <div className="text-center max-w-md px-6">
          <div
            className="mx-auto w-14 h-14 rounded-xl flex items-center justify-center mb-4"
            style={{ backgroundColor: '#18559B' }}
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style={{ color: '#fff' }}>
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" fill="currentColor" />
              <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <h3
            className="text-base font-semibold mb-2"
            style={{ color: 'var(--text-primary)' }}
          >
            Word-документ: {file.name}
          </h3>
          <p
            className="text-sm mb-4"
            style={{ color: 'var(--text-secondary)' }}
          >
            {fileExtension === 'doc'
              ? 'Формат .doc требует конвертации для просмотра в браузере.'
              : 'Полный рендеринг Word-документов требует сторонней библиотеки или сервиса.'}
          </p>

          <div
            className="p-3 rounded-lg mb-4 text-sm"
            style={{ backgroundColor: 'var(--bg-surface-2)', color: 'var(--text-secondary)' }}
          >
            <p className="font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
              Доступные варианты:
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>Скачать файл и открыть в Microsoft Word</li>
              <li>Открыть в Google Docs или Office Online</li>
              <li>Использовать конвертер в PDF</li>
            </ul>
          </div>

          <div className="flex gap-2 justify-center">
            <a
              href={fileUrl}
              download={file.name}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              style={{
                backgroundColor: 'var(--accent-engineering)',
                color: 'var(--text-inverse)',
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Скачать
            </a>
            <a
              href={`https://docs.google.com/gview?url=${encodeURIComponent(fileUrl)}&embedded=true`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              style={{
                backgroundColor: 'var(--bg-surface-2)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-default)',
              }}
            >
              Открыть в Google Docs
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Если mammoth успешно конвертировал - показываем HTML
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

        <div className="flex items-center gap-2">
          <a
            href={fileUrl}
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
      </div>

      {/* Document Content */}
      <div
        className="flex-1 overflow-auto p-4"
        style={{ backgroundColor: '#525659' }}
      >
        <div
          className="max-w-3xl mx-auto bg-white shadow-lg rounded"
          dangerouslySetInnerHTML={{ __html: content || '' }}
          style={{
            minHeight: '800px',
            padding: '40px',
            fontFamily: 'Georgia, serif',
            lineHeight: '1.6',
          }}
        />
      </div>

      {/* Footer */}
      <div
        className="px-4 py-1.5 border-t text-xs text-center shrink-0"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-default)' }}
      >
        <span style={{ color: 'var(--text-tertiary)' }}>
          {file.name} · Просмотр через mammoth.js (базовое форматирование)
        </span>
      </div>
    </div>
  );
}
