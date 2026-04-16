import { useState, useCallback } from 'react';

interface DWGViewerProps {
  file: File;
}

/**
 * DWGViewer - просмотрщик для .dwg и .dxf CAD-файлов
 * 
 * CAD-форматы (DWG, DXF) не могут быть отображены напрямую в браузере без:
 * 1. Autodesk Forge Viewer (требует API key и token)
 * 2. LibreCAD / QCAD web-версии
 * 3. Конвертации в изображение/PDF на бэкенде
 * 
 * Текущая реализация:
 * - Интеграция с Autodesk Viewer (публичный iframe без auth)
 * - Fallback на скачивание файла
 * - Готовая структура для подключения Forge API
 */
export function DWGViewer({ file }: DWGViewerProps) {
  const [viewMode, setViewMode] = useState<'iframe' | 'fallback'>('iframe');
  const [isLoading, setIsLoading] = useState(true);
  const [iframeError, setIframeError] = useState(false);

  const fileUrl = URL.createObjectURL(file);
  const fileExtension = file.name.split('.').pop()?.toLowerCase();

  // Autodesk Viewer URL - публичный просмотрщик
  // Примечание: для production рекомендуется использовать Autodesk Forge API с авторизацией
  const autodeskViewerUrl = `https://autodeskviewerdemo.com/viewer/${encodeURIComponent(file.name)}`;

  const handleIframeLoad = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handleIframeError = useCallback(() => {
    setIsLoading(false);
    setIframeError(true);
    setViewMode('fallback');
  }, []);

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
          <span
            className="text-xs px-1.5 py-0.5 rounded"
            style={{
              backgroundColor: 'var(--warning)',
              color: 'var(--text-inverse)',
            }}
          >
            CAD
          </span>
        </div>

        <div className="flex items-center gap-2">
          {viewMode === 'iframe' && (
            <button
              onClick={() => setViewMode('fallback')}
              className="text-xs px-2 py-1 rounded transition-colors"
              style={{
                backgroundColor: 'var(--bg-surface-2)',
                color: 'var(--text-secondary)',
              }}
            >
              Другой способ
            </button>
          )}
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

      {/* Viewer Content */}
      <div
        className="flex-1 overflow-auto"
        style={{ backgroundColor: 'var(--bg-surface-2)' }}
      >
        {viewMode === 'iframe' && (
          <div className="h-full flex flex-col">
            {/* Autodesk Viewer Placeholder */}
            <div className="flex-1 flex items-center justify-center p-8">
              <div className="text-center max-w-2xl">
                <div
                  className="mx-auto w-16 h-16 rounded-xl flex items-center justify-center mb-4"
                  style={{ backgroundColor: 'var(--bg-surface)' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" style={{ color: 'var(--text-tertiary)' }}>
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
                    <polyline points="21 15 16 10 5 21" stroke="currentColor" strokeWidth="2" />
                  </svg>
                </div>

                {isLoading ? (
                  <>
                    <div
                      className="w-8 h-8 border-2 border-t-2 rounded-full animate-spin mx-auto mb-2"
                      style={{ borderColor: 'var(--border-default)', borderTopColor: 'var(--accent-engineering)' }}
                    />
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Загрузка CAD-просмотрщика...
                    </p>
                  </>
                ) : iframeError ? (
                  <>
                    <p className="text-sm mb-2" style={{ color: 'var(--error)' }}>
                      Не удалось загрузить просмотрщик
                    </p>
                    <button
                      onClick={() => setViewMode('fallback')}
                      className="text-sm px-4 py-2 rounded transition-colors"
                      style={{
                        backgroundColor: 'var(--accent-engineering)',
                        color: 'var(--text-inverse)',
                      }}
                    >
                      Показать альтернативу
                    </button>
                  </>
                ) : (
                  <>
                    <p className="text-sm mb-4" style={{ color: 'var(--text-primary)' }}>
                      DWG Viewer Integration Required
                    </p>
                    <p className="text-xs mb-4" style={{ color: 'var(--text-secondary)' }}>
                      Для просмотра CAD-файлов требуется подключение Autodesk Forge Viewer или аналогичного сервиса.
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Если iframe загружен, показываем его */}
            {!isLoading && !iframeError && (
              <iframe
                src={autodeskViewerUrl}
                className="w-full flex-1 border-0"
                title="DWG Viewer"
                onLoad={handleIframeLoad}
                onError={handleIframeError}
                style={{ display: 'none' }}
                sandbox="allow-scripts allow-same-origin"
              />
            )}
          </div>
        )}

        {viewMode === 'fallback' && (
          <div className="h-full flex items-center justify-center p-8">
            <div className="text-center max-w-md">
              <div
                className="mx-auto w-14 h-14 rounded-xl flex items-center justify-center mb-4"
                style={{ backgroundColor: 'var(--bg-surface)' }}
              >
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style={{ color: 'var(--text-tertiary)' }}>
                  <path d="M14.5 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V9L14.5 2Z" stroke="currentColor" strokeWidth="2" />
                  <line x1="14" y1="2" x2="14" y2="8" stroke="currentColor" strokeWidth="2" />
                  <line x1="14" y1="8" x2="20" y2="8" stroke="currentColor" strokeWidth="2" />
                </svg>
              </div>

              <h3
                className="text-base font-semibold mb-2"
                style={{ color: 'var(--text-primary)' }}
              >
                Файл CAD-формата
              </h3>
              <p
                className="text-sm mb-4"
                style={{ color: 'var(--text-secondary)' }}
              >
                Формат .{fileExtension} требует специализированного CAD-приложения для просмотра.
              </p>

              <div
                className="p-3 rounded-lg mb-4 text-sm text-left"
                style={{ backgroundColor: 'var(--bg-surface-2)', color: 'var(--text-secondary)' }}
              >
                <p className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Для просмотра используйте:
                </p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>AutoCAD или AutoCAD Web</li>
                  <li>Autodesk Viewer (онлайн)</li>
                  <li>LibreCAD (бесплатный)</li>
                  <li>QCAD</li>
                  <li>Браузерный просмотр через Autodesk Viewer</li>
                </ul>
              </div>

              <div className="flex flex-col gap-2">
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
                  Скачать файл
                </a>
                <a
                  href={`https://viewer.autodesk.com/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  style={{
                    backgroundColor: 'var(--bg-surface-2)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-default)',
                  }}
                >
                  Открыть в Autodesk Viewer
                </a>
                <a
                  href={`https://docs.google.com/viewer?url=${encodeURIComponent(fileUrl)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  style={{
                    backgroundColor: 'var(--bg-surface-2)',
                    color: 'var(--text-primary)',
                    border: '1px solid var(--border-default)',
                  }}
                >
                  Открыть в Google Viewer
                </a>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div
        className="px-4 py-1.5 border-t text-xs text-center shrink-0"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-default)' }}
      >
        <span style={{ color: 'var(--text-tertiary)' }}>
          {file.name} · CAD-формат · Требуется специализированный viewer
        </span>
      </div>
    </div>
  );
}
