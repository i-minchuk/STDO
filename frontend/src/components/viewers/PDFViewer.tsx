import { useState, useCallback, useRef, useEffect } from 'react';
import * as pdfjsLib from 'pdfjs-dist';

// Настройка worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

interface PDFViewerProps {
  file: File;
}

export function PDFViewer({ file }: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfDoc, setPdfDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const fileUrl = URL.createObjectURL(file);

  // Загрузка PDF документа
  useEffect(() => {
    const loadPDF = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const loadingTask = pdfjsLib.getDocument(fileUrl);
        const pdf = await loadingTask.promise;
        
        setPdfDoc(pdf);
        setTotalPages(pdf.numPages);
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Не удалось загрузить PDF');
        setIsLoading(false);
      }
    };

    loadPDF();

    return () => {
      URL.revokeObjectURL(fileUrl);
    };
  }, [fileUrl]);

  // Отрисовка страницы
  useEffect(() => {
    if (!pdfDoc || !canvasRef.current) return;

    const renderPage = async (pageNum: number) => {
      try {
        const page = await pdfDoc.getPage(pageNum);
        const canvas = canvasRef.current;
        
        if (!canvas) return;

        const viewport = page.getViewport({ scale });
        
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderTask = page.render({
          canvasContext: canvas.getContext('2d')!,
          viewport,
        } as any);
        
        await renderTask.promise;
      } catch (err) {
        console.error('Ошибка отрисовки страницы:', err);
      }
    };

    renderPage(currentPage);
  }, [pdfDoc, currentPage, scale]);

  const goToPreviousPage = useCallback(() => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  }, []);

  const goToNextPage = useCallback(() => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  }, [totalPages]);

  const zoomIn = useCallback(() => {
    setScale((prev) => Math.min(prev + 0.25, 3.0));
  }, []);

  const zoomOut = useCallback(() => {
    setScale((prev) => Math.max(prev - 0.25, 0.5));
  }, []);

  if (error) {
    return (
      <div
        className="flex-1 flex items-center justify-center"
        style={{ backgroundColor: 'var(--bg-app)' }}
      >
        <div className="text-center">
          <p className="text-sm mb-2" style={{ color: 'var(--error)' }}>
            Ошибка загрузки PDF: {error}
          </p>
          <a
            href={fileUrl}
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

        <div className="flex items-center gap-1">
          <button
            onClick={zoomOut}
            disabled={scale <= 0.5}
            className="p-1.5 rounded transition-colors disabled:opacity-50"
            style={{ color: 'var(--text-secondary)' }}
            title="Уменьшить масштаб"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
              <line x1="8" y1="11" x2="14" y2="11" />
            </svg>
          </button>

          <span
            className="text-xs font-medium px-2"
            style={{ color: 'var(--text-primary)' }}
          >
            {Math.round(scale * 100)}%
          </span>

          <button
            onClick={zoomIn}
            disabled={scale >= 3.0}
            className="p-1.5 rounded transition-colors disabled:opacity-50"
            style={{ color: 'var(--text-secondary)' }}
            title="Увеличить масштаб"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
              <line x1="11" y1="8" x2="11" y2="14" />
              <line x1="8" y1="11" x2="14" y2="11" />
            </svg>
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={goToPreviousPage}
            disabled={currentPage <= 1}
            className="p-1.5 rounded transition-colors disabled:opacity-50"
            style={{ color: 'var(--text-secondary)' }}
            title="Предыдущая страница"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 8 12 15 6" />
            </svg>
          </button>

          <span
            className="text-xs font-medium"
            style={{ color: 'var(--text-primary)' }}
          >
            {currentPage} / {totalPages || '-'}
          </span>

          <button
            onClick={goToNextPage}
            disabled={currentPage >= totalPages}
            className="p-1.5 rounded transition-colors disabled:opacity-50"
            style={{ color: 'var(--text-secondary)' }}
            title="Следующая страница"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 16 12 9 6" />
            </svg>
          </button>
        </div>

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

      {/* PDF Content */}
      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4"
        style={{ backgroundColor: '#525659', display: 'flex', justifyContent: 'center' }}
      >
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div
                className="w-8 h-8 border-2 border-t-2 rounded-full animate-spin mx-auto mb-2"
                style={{ borderColor: 'var(--border-default)', borderTopColor: 'var(--accent-engineering)' }}
              />
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Загрузка PDF...
              </p>
            </div>
          </div>
        )}

        {!isLoading && !error && pdfDoc && (
          <canvas
            ref={canvasRef}
            className="shadow-lg"
            style={{ maxHeight: 'calc(100vh - 200px)' }}
          />
        )}
      </div>

      {/* Footer */}
      <div
        className="px-4 py-1.5 border-t text-xs text-center shrink-0"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border-default)' }}
      >
        {totalPages > 0 && (
          <span style={{ color: 'var(--text-tertiary)' }}>
            {file.name} · {totalPages} страниц
          </span>
        )}
      </div>
    </div>
  );
}
