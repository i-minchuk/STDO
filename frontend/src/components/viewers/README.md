# Document Viewers - STDO

Компоненты для просмотра документов в центральной рабочей области workspace.

## Архитектура

### DocumentViewerHost

Единый host-компонент, который:
- Принимает выбранный документ через active tab
- Определяет тип файла (по расширению и mime type)
- Рендерит соответствующий viewer компонент
- Показывает состояния: loading, error, empty, unsupported

### Определение типа файла

```typescript
// В DocumentViewerHost/detectFileType()
- PDF: mimeType === 'application/pdf' || extension === 'pdf'
- Image: mimeType.startsWith('image/') || extensions: png, jpg, jpeg, webp, svg, tiff, gif
- Excel: mimeType.includes('excel') || extensions: xls, xlsx, xlsm
- Word: mimeType.includes('word') || extensions: doc, docx
- DWG: extensions: dwg, dxf
- CSV: extension === 'csv' || mimeType === 'text/csv'
```

## Поддерживаемые форматы

### 1. PDF Viewer (`PDFViewer.tsx`)

**Библиотека:** `pdfjs-dist`

**Функциональность:**
- Просмотр страниц с навигацией (prev/next)
- Масштабирование (0.5x - 3.0x)
- Отображение текущего номера страницы и общего количества
- Адаптивный рендеринг на canvas
- Загрузка с индикатором прогресса
- Обработка ошибок с возможностью скачивания

**Интеграция:**
```typescript
import { PDFViewer } from '@/components/viewers';

<PDFViewer file={file} />
```

### 2. Image Viewer (`ImageViewer.tsx`)

**Библиотека:** Native (HTML5 img + CSS transform)

**Функциональность:**
- Просмотр изображений всех поддерживаемых форматов
- Масштабирование (0.25x - 4.0x)
- Поворот на ±90°
- Сброс view (zoom/rotation)
- Drag-to-pan (заготовка)
- Адаптивное отображение (contain)

**Интеграция:**
```typescript
import { ImageViewer } from '@/components/viewers';

<ImageViewer file={file} />
```

### 3. Excel Viewer (`ExcelViewer.tsx`)

**Библиотека:** `xlsx` (SheetJS)

**Функциональность:**
- Парсинг .xls и .xlsx файлов
- Отображение multiple sheets с табами
- Рендеринг таблицы с headers и строками
- Поддержка пустых ячеек
- Индикация количества строк в footer

**Интеграция:**
```typescript
import { ExcelViewer } from '@/components/viewers';

<ExcelViewer file={file} />
```

### 4. Word Viewer (`WordViewer.tsx`)

**Библиотека:** `mammoth.js` (для .docx), fallback для .doc

**Функциональность:**
- Конвертация .docx в HTML через mammoth.js
- Базовое форматирование (заголовки, параграфы, списки)
- Fallback страница для .doc и когда mammoth недоступен
- Кнопки "Скачать" и "Открыть в Google Docs"
- Честное уведомление о ограничениях

**Fallback Strategy:**
1. Попытка загрузки через mammoth.js
2. Если не удалось → показать fallback UI
3. Предложить скачать файл или открыть в Google Docs/Office Online

**Интеграция:**
```typescript
import { WordViewer } from '@/components/viewers';

<WordViewer file={file} />
```

### 5. DWG Viewer (`DWGViewer.tsx`)

**Библиотека:** Autodesk Viewer (iframe), fallback

**Функциональность:**
- Интеграция с Autodesk Viewer через iframe (заготовка)
- Fallback UI с перечнем альтернатив
- Кнопки: скачать, Autodesk Viewer, Google Viewer
- Метка "CAD" в toolbar

**Важно:**
Для полноценного просмотра DWG файлов в production требуется:
- Autodesk Forge API с авторизацией
- Либо бэкенд-конвертация в PDF/image
- Либо интеграция с LibreCAD/QCAD web

**Текущий fallback:**
```
┌──────────────────────────────────────┐
│  Файл CAD-формата                    │
│                                      │
│  Для просмотра используйте:          │
│  • AutoCAD или AutoCAD Web           │
│  • Autodesk Viewer (онлайн)          │
│  • LibreCAD (бесплатный)             │
│  • QCAD                              │
│  • Браузерный просмотр               │
│                                      │
│  [Скачать файл] [Autodesk Viewer]    │
└──────────────────────────────────────┘
```

### 6. CSV Viewer (`CSVViewer.tsx`)

**Функциональность:**
- Уведомление о необходимости внешнего приложения
- Кнопка скачивания

## Использование

### В EditorArea

```typescript
import DocumentViewerHost from '@/components/viewers/DocumentViewerHost';

export default function EditorArea() {
  const { activeTab, openTabs } = useWorkspaceStore();
  
  if (!activeTab) {
    return <EmptyState />;
  }

  return (
    <div className="flex-1 overflow-hidden">
      <DocumentViewerHost />
    </div>
  );
}
```

### Передача файла в Tab

```typescript
// При создании вкладки
addTab({
  id: `doc-${Date.now()}`,
  type: 'document',
  title: file.name,
  file: file, // File объект для viewer
});
```

## Состояния Viewer

### Empty State
- Нет выбранного документа
- Иконка + подсказка "Выберите документ из Explorer"

### Loading State
- Индикатор загрузки (spinner)
- Текст "Загрузка..."

### Error State
- Сообщение об ошибке
- Кнопка "Скачать файл"

### Unsupported Format
- Иконка файла
- Сообщение "Формат не поддерживается"
- Кнопка "Скачать файл"

## Расширяемость

### Добавление нового формата

1. Создайте компонент `NewFormatViewer.tsx`:
```typescript
interface NewFormatViewerProps {
  file: File;
}

export function NewFormatViewer({ file }: NewFormatViewerProps) {
  // Реализация viewer
}
```

2. Добавьте определение типа в `DocumentViewerHost`:
```typescript
function detectFileType(file: File): FileType {
  if (extension === 'newext') return 'newformat';
  // ...
}
```

3. Добавьте case в switch:
```typescript
switch (fileType) {
  case 'newformat':
    return <NewFormatViewer file={file} />;
  // ...
}
```

## Зависимости

```json
{
  "pdfjs-dist": "^4.x",
  "@react-pdf/renderer": "^4.x",
  "xlsx": "^0.18.x",
  "mammoth": "^1.6.x"
}
```

## Известные ограничения

1. **DWG**: Полноценный просмотр требует Autodesk Forge API
2. **Word (.doc)**: Требует конвертации на бэкенде
3. **CSV**: Только базовый placeholder
4. **TIFF**: Может требовать дополнительной библиотеки для рендеринга

## Будущие улучшения

- [ ] Поддержка аннотаций и комментариев в PDF
- [ ] Поиск по тексту PDF
- [ ] Экспорт в другие форматы
- [ ] Интеграция с Autodesk Forge API
- [ ] Поддержка больше CAD-форматов (DWF, DXF)
- [ ] Онлайн-редактирование Word/Excel
