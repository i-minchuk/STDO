# Document Workspace UX Specification

## A. UX-решение

### Новая модель экрана "Рабочее пространство документов"

**Три-панельная архитектура + нижняя панель:**

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            СТРАНИЦА ДОКУМЕНТА                                 │
├─────────────┬──────────────────────────────────────┬──────────────────────────┤
│   ЛЕВАЯ     │               ЦЕНТР                  │         ПРАВАЯ           │
│   ПАНЕЛЬ    │                                      │         ПАНЕЛЬ           │
│             │  ┌────────────────────────────────┐  │                        │
│  Дерево     │  │ TOOLBAR                        │  │  Замечания             │
│  документов │  │ [Создать ревизию]              │  │  ──────────────────   │
│             │  │ [На согласование] [На проверку]│  │  • Список             │
│  - Проекты  │  │ [Zoom] [Page] [DL]             │  │  • Фильтры            │
│  - Этапы    │  └────────────────────────────────┘  │  • Счётчики           │
│  - Киты     │  ┌────────────────────────────────┐  │  • Действия           │
│  - Докум.   │  │                                │  │                        │
│  - Файлы    │  │         VIEWER AREA            │  │  [Новое замечание]    │
│             │  │                                │  │                        │
│  [Создать   │  │  PDF / Image / Excel / Word /  │  │                        │
│   документ] │  │  DWG Fallback                  │  │                        │
│             │  │                                │  │                        │
│  [Active    │  └────────────────────────────────┘  │                        │
│   state]    │                                      │                        │
├─────────────┴──────────────────────────────────────┴──────────────────────────┤
│                         НИЖНЯЯ ПАНЕЛЬ СТРАНИЦЫ                                │
│  История / Связи / Версии / Метаданные / Логи / Доп. действия                │
│  (часть layout страницы, закреплена в общей высоте, не уезжает вниз)         │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Порядок действий в toolbar (жизненный цикл документа):**

1. **Создать ревизию** — создание новой версии документа
2. **Отправить на согласование** — переход статуса "На согласование"
3. **Отправить на проверку** — переход статуса "На проверку"
4. **Zoom** — управление масштабом
5. **Page** — навигация по страницам (для PDF)
6. **Download** — скачивание файла

**Ключевые требования:**

- Кнопка "Создать документ" всегда в левой панели (Explorer), независимо от состояния viewer
- Нижняя панель — часть основного layout страницы, всегда остаётся в пределах рабочей области
- Toolbar отображается только при выбранном документе

**Роли панелей:**

| Панель | Роль | Контент |
|--------|------|---------|
| **Левая** | Навигация и выбор | Дерево проектов/этапов/китов/документов с явным active state |
| **Центр** | Просмотр содержимого | Viewer для файлов + честный fallback для неподдерживаемых форматов |
| **Правая** | Рецензирование | Замечания по текущему документу (только review-related сущности) |

**Основные пользовательские сценарии:**

1. **Открытие документа из дерева**: Клик по документу → viewer загружает файл → правая панель показывает замечания по этому document_id
2. **Переключение между документами**: Новый клик обновляет центр и правую панель, сохраняя левое дерево
3. **Добавление замечания**: Форма внизу правой панели → замечание привязывается к active document_id
4. **Загрузка нового файла**: Drag&drop в центр или кнопка "Загрузить" → открывается в новой вкладке
5. **Создание документа**: Через `/documents/new` → выбор категории → выбор шаблона → ввод деталей → документ создан

---

## B. Состояния и правила

### Viewer Resolution Pipeline

| Тип файла (расширение) | Viewer | Toolbar | Loading | Error | Fallback |
|------------------------|--------|---------|---------|-------|----------|
| `.pdf` | PDFViewer (pdf.js) | Zoom, Pages, Download | Spinner + "Загрузка PDF..." | "Ошибка загрузки" + кнопка скачать | N/A |
| `.png`, `.jpg`, `.gif`, `.svg`, `.webp` | ImageViewer | Zoom, Fit, Download | Spinner + "Загрузка изображения..." | "Не удалось загрузить" + скачать | N/A |
| `.xlsx`, `.xls` | ExcelViewer | Sheets, Download | Spinner + "Загрузка таблицы..." | "Ошибка парсинга" + скачать | N/A |
| `.docx`, `.doc` | WordViewer (mammoth) | Download | Spinner + "Загрузка документа..." | "Не поддерживается" + скачать | Скачать файл |
| `.dwg`, `.dxf` | DWGViewer | Download only | N/A (fallback сразу) | N/A | **Честный fallback**: "CAD-формат требует специализированного viewer" + кнопки [Скачать] [Autodesk Viewer] + список альтернатив |
| `.csv` | CSVViewer | Download | Spinner | Ошибка | N/A |
| Неподдерживаемый | UnsupportedViewer | Download only | N/A | N/A | "Формат не поддерживается" + скачать |
| Нет файла | EmptyState | Hidden | N/A | N/A | "Выберите документ из Explorer" |

### MIME/Extension-based Rules

```typescript
// Определение типа файла
export const detectType = (fileName: string): ViewerType => {
  const ext = fileName.split('.').pop()?.toLowerCase();

  if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'tiff'].includes(ext!)) return 'image';
  if (ext === 'pdf') return 'pdf';
  if (['xls', 'xlsx', 'xlsm'].includes(ext!)) return 'excel';
  if (['doc', 'docx'].includes(ext!)) return 'word';
  if (ext === 'dwg' || ext === 'dxf') return 'dwg';
  if (ext === 'csv') return 'csv';

  return 'unsupported'; // Явный unsupported вместо default pdf
};

// Проверка на native preview support
export const hasNativePreview = (type: ViewerType): boolean => {
  return VIEWER_CONFIGS[type].supportsPreview;
};
```

### Node Type → Behavior

| Тип узла в дереве | Поведение при клике |
|-------------------|---------------------|
| `document` | Открыть в viewer, активировать таб, показать замечания по document_id |
| `folder`/`project`/`stage`/`kit`/`section` | Expand/collapse, не открывать viewer |
| `remark` | Прокрутить к замечанию в правой панели (future) |

### Remarks Panel States

| Состояние | UI |
|-----------|-----|
| documentId = null | Empty state: "Выберите документ для просмотра замечаний" |
| Нет замечаний | "Нет замечаний по документу" + кнопка "Добавить замечание" |
| Замечания есть | Список с фильтрами (все/открыто/решено/отклонено/снято), счетчики |
| Загрузка | Skeleton карточки замечаний |
| Ошибка | "Не удалось загрузить замечания" |

### Loading/Error/Empty States

| Компонент | Loading | Error | Empty |
|-----------|---------|-------|-------|
| Viewer | Spinner + "Загрузка {тип}..." | "Ошибка: {сообщение}" + кнопка скачать | "Выберите документ из дерева" |
| RemarksPanel | Skeleton карточек | "Не удалось загрузить замечания" | "Нет замечаний по документу" |
| Explorer | Skeleton узлов | "Не удалось загрузить дерево" | "Нет документов в проекте" |

---

## C. Изменения в UI

### Блоки для удаления:

1. **Из DocumentDetail.tsx (если используется)**:
   - Вкладка "Задачи" → переместить в bottom panel или отдельную страницу
   - Вкладка "Журнал изменений" → переместить в bottom panel
   - Выбор шаблона → перенести в DocumentCreate

2. **Из RemarksPanel**:
   - Общие свойства документа (не связаны с review)
   - Системные виджеты "на всякий случай"

3. **Из DocumentCreate**:
   - Убрать placeholder "будет доступно"

### Блоки для перемещения:

| Блок | Откуда | Куда | Обоснование |
|------|--------|------|-------------|
| Свойства документа | DocumentDetail tabs | DocumentMetadataBar (top) | Metadata всегда виден при просмотре |
| История ревизий | DocumentDetail tabs | Bottom panel или отдельная вкладка | Не критично для review flow |
| Выбор шаблона | DocumentDetail | DocumentCreate | Шаблон — часть инициализации сущности |

### Компоненты для добавления:

1. **DocumentWorkspace.tsx** — единый сценарий работы с документами
2. **DocumentLoadingState** — skeleton loader для viewer
3. **DocumentErrorState** — error UI с кнопкой повторной загрузки
4. **EmptyViewerState** — ясное сообщение при отсутствии выбора
5. **EmptyInspector** — placeholder правой панели при отсутствии документа

### Переименования:

| Старое имя | Новое имя | Обоснование |
|------------|-----------|-------------|
| `InspectorPanel` | `RemarksPanel` | Явная семантика: панель для замечаний |
| `ExplorerSidebar` | `DocumentTree` | Ясность: дерево документов |
| `DocumentViewerHost` (legacy) | Сохранить как интеграционную точку | Backward compatibility |

---

## D. Изменения в frontend-логике

### State Model

```typescript
interface SelectedDocument {
  id: number;
  code: string;
  title: string;
  fileUrl?: string;
  fileName: string;
  project_id: number;
  status?: string;
  doc_type?: string;
  discipline?: string;
}

interface DocumentWorkspaceState {
  // Активный документ — single source of truth
  selectedDocument: SelectedDocument | null;
  
  // Viewer state (выводится из selectedDocument)
  viewerState: {
    fileUrl: string | null;
    fileName: string;
    fileType: ViewerType;
    isLoading: boolean;
    error: string | null;
  };
  
  // Remarks state
  remarksState: {
    remarks: Remark[];
    filter: RemarkStatus | 'all';
    isLoading: boolean;
  };
  
  // Tree state
  treeState: {
    nodes: ExplorerNode[];
    expandedNodes: Set<string>;
    activeNodeId: string | null;
  };
}
```

### Event Flow

```
[Клик по документу в дереве]
  ↓
[onNodeClick(nodeId, 'document', documentId)]
  ↓
[setActiveExplorerNode(nodeId)]
  ↓
[fetchDocument(documentId)]
  ↓
[setSelectedDocument({ id, code, title, fileUrl, fileName, ... })]
  ↓
[openTab({ id: documentId, type: 'document', title: code, file, documentId })]
  ↓
[fetchRemarks(documentId)]
  ↓
[setRemarksState(remarks)]
  ↓
[Viewer рендерится с правильным типом]
```

### Связь состояний

```typescript
// Единый источник истины — selectedDocument
const selectedDocument = workspaceStore.selectedDocument;

// Viewer зависит от selectedDocument.fileUrl
const viewerProps = {
  fileUrl: selectedDocument?.fileUrl,
  fileName: selectedDocument?.fileName,
  mock: !selectedDocument?.fileUrl,
  documentId: selectedDocument?.id
};

// RemarksPanel зависит от selectedDocument.id
const remarksProps = {
  documentId: selectedDocument?.id,
  projectId: selectedDocument?.project_id
};

// Toolbar зависит от viewer type
const toolbarProps = {
  fileType: detectType(selectedDocument?.fileName),
  showZoom: hasNativePreview(fileType),
  onDownload: handleDownload
};
```

### Edge Cases

1. **Повторный клик по тому же документу** → No-op (проверка `if (selectedDocument?.id === documentId) return`)
2. **Клик по папке** → Expand/collapse, не открывать viewer
3. **Закрытие активного документа** → Активировать предыдущий таб или показать empty state
4. **Потеря связи с сервером** → Показать error state в viewer с кнопкой "Попробовать снова"
5. **Большой файл** → Skeleton loader + прогресс (если API поддерживает)
6. **Отсутствие файла у документа** → Показать "Файл не загружен" с кнопкой "Загрузить ревизию"
7. **Переключение проекта** → Сброс selectedDocument, очистка замечаний

---

## E. Acceptance Criteria

### Viewer функциональность

| Критерий | Проверка |
|----------|----------|
| При клике на PDF из дерева он открывается в центре | 1 клик → viewer рендерит PDF |
| PDF viewer поддерживает zoom in/out (0.5x - 3.0x) | Toolbar кнопки работают |
| PDF viewer поддерживает навигацию по страницам | Prev/Next/Page X of Y |
| Изображения корректно fit/zoom | object-fit: contain, max-width/max-height |
| Excel показывает таблицы с листами | Sheet tabs переключаются |
| Word показывает базовый контент | mammoth рендерит текст |
| DWG показывает честный fallback | Фраза "CAD-формат требует специализированного viewer" + кнопки [Скачать] [Autodesk Viewer] |
| Неподдерживаемый формат → fallback | "Формат не поддерживается" + скачать |
| Loading state показывает spinner + текст | "Загрузка PDF..." / "Загрузка изображения..." |
| Error state показывает сообщение + действие | "Ошибка: {msg}" + кнопка скачать/повторить |

### Навигация и states

| Критерий | Проверка |
|----------|----------|
| При клике на документ он получает active state в дереве | Фон узла меняется |
| Центральная область обновляется не более чем за 2 сек | Viewer рендерится |
| Правая панель показывает замечания по выбранному документу | document_id привязан |
| Повторный клик по тому же документу не перезагружает | No-op |
| Клик по папке только expand/collapse | Viewer не открывается |
| Закрытие документа активирует предыдущий таб | Или empty state |
| Состояние сохраняется при переключении между документами | Zoom, страница, фильтр замечаний |

### Правая панель (Remarks)

| Критерий | Проверка |
|----------|----------|
| Правая панель никогда не показывает выбор шаблона | Шаблоны только в DocumentCreate |
| Правая панель привязана к active document_id | При смене документа замечания обновляются |
| Фильтры работают (все/открыто/решено/отклонено/снято) | Список фильтруется |
| Счетчики отражают реальное количество | Counts обновляются |
| Новое замечание привязывается к документу | document_id в payload |
| Пустое состояние ясное | "Нет замечаний по документу" |

### Layout и масштабирование

| Критерий | Проверка |
|----------|----------|
| Zoom не ломает layout на типовых разрешениях | 1366x768, 1920x1080, 2560x1440 |
| Нет двойных scroll-контейнеров | Один scroll в viewer area |
| Сайдбары можно ресайзить | Explorer/Inspector width меняется |
| При collapsed sidebar центральная область расширяется | Flex layout работает |
| Bottom panel не накладывается на viewer | z-index correct |
| Viewer корректно fit при изменении размера окна | window.resize |

### Создание документа

| Критерий | Проверка |
|----------|----------|
| Выбор шаблона только в создании | Не в просмотре/редактировании |
| Flow: категория → шаблон → детали | 3 шага |
| После создания документ открывается в центре | redirect to /documents/:id |
| Шаблон предзаполняет поля | doc_type, discipline |
| Можно пропустить выбор шаблона | Кнопка "Пропустить" |

---

## F. Self-QA checklist

### Функциональное тестирование

- [ ] **Открытие PDF**: Клик → viewer → zoom → pages → download
- [ ] **Открытие изображения**: Клик → viewer → fit/zoom → download
- [ ] **Открытие Excel**: Клик → viewer → sheet tabs → download
- [ ] **Открытие Word**: Клик → viewer → content → download
- [ ] **Открытие DWG**: Клик → fallback → скачать/открыть во внешнем viewer
- [ ] **Открытие неподдерживаемого**: Клик → fallback → скачать
- [ ] **Переключение между документами**: doc1 → doc2 → замечания обновляются
- [ ] **Повторный клик**: doc1 → doc1 → no reload
- [ ] **Клик по папке**: folder → expand → viewer не открывается
- [ ] **Закрытие документа**: close tab → prev tab активен или empty state

### State тестирование

- [ ] **Loading state**: PDF большой → spinner + "Загрузка PDF..."
- [ ] **Error state**: Неправильный URL → "Ошибка" + кнопка
- [ ] **Empty state**: Нет выбора → "Выберите документ"
- [ ] **No remarks**: Документ без замечаний → "Нет замечаний"
- [ ] **Filtered remarks**: Фильтр "открыто" → только открытые

### Layout тестирование

- [ ] **Zoom 0.5x - 3.0x**: Все масштабы работают без overflow
- [ ] **Resizing sidebar**: Explorer шире/уже → центр адаптируется
- [ ] **Collapsed sidebar**: explorerCollapsed → центр занимает место
- [ ] **Window resize**: browser resize → viewer fit
- [ ] **Multiple monitors**: 1920x1080 + 1366x768 → корректно

### Accessibility

- [ ] **Keyboard navigation**: Tab → Enter на узлах дерева
- [ ] **ARIA labels**: role="tree", role="treeitem", aria-expanded
- [ ] **Focus states**: active узел имеет focus ring
- [ ] **Error messages**: читаемые, с действием

### Performance

- [ ] **Large PDF**: 50+ страниц → рендер не блокирует UI
- [ ] **Large image**: 4K изображение → fit без lag
- [ ] **Many remarks**: 100+ замечаний → scroll плавный
- [ ] **Tree depth**: 5 уровней вложенности → expand instant

### Cross-browser

- [ ] **Chrome 120+**: Все функции работают
- [ ] **Firefox 120+**: Все функции работают
- [ ] **Safari 17+**: PDF viewer работает
- [ ] **Edge 120+**: Все функции работают

---

## G. Файлы для внедрения

### Созданы:

1. `STDO/frontend/src/components/workspace/DocumentWorkspace.tsx` — единый сценарий
2. `STDO/frontend/src/components/workspace/types/workspace.types.ts` — обновлены типы
3. `STDO/frontend/src/components/workspace/store/workspaceStore.ts` — selectedDocument
4. `STDO/frontend/src/components/viewers/types.ts` — supportsPreview, unsupported
5. `STDO/frontend/src/components/RemarksPanel.tsx` — documentId support
6. `STDO/frontend/src/components/workspace/ExplorerSidebar.tsx` — onNodeClick callback
7. `STDO/frontend/src/api/documents.ts` — getRemarksByDocument
8. `STDO/frontend/src/pages/DocumentCreate.tsx` — шаблон на этапе создания

### Требуется интеграция:

1. Подключить `DocumentWorkspace` в роутинг вместо `DocumentDetail`
2. Добавить API endpoint `/api/remarks/document/:documentId`
3. Настроить file upload для revision file_path
4. Добавить реальные fileUrl из БД

---

## H. Допущения и спорные места

1. **File URL формирование**: Предполагается `/api/files/{file_path}` — уточнить у backend
2. **MIME type для DWG**: `application/acad` — может потребовать корректировки
3. **Отсутствие реальных файлов**: Сейчас моки — нужно подключить upload
4. **Аутентификация в API**: localStorage token — проверить актуальность
5. **Пагинация замечаний**: Сейчас все замечания — добавить pagination при >100

---

**Документ готов к реализации.**
