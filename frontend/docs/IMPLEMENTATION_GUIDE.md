# Document Workspace — Руководство по внедрению

## Краткое описание

Документ описывает процесс внедрения единого сценария работы с документами в центральную область приложения с поддержкой:
- **Viewer** для PDF, изображений, Excel, Word, DWG (fallback)
- **Дерево документов** в левой панели с active state
- **Замечания** в правой панели, привязанные к документу
- **Честный fallback** для неподдерживаемых форматов
- **Выбор шаблона** только на этапе создания документа

---

## Готовые компоненты

Все основные компоненты уже созданы:

| Компонент | Путь | Описание |
|-----------|------|----------|
| `DocumentWorkspace` | `src/components/workspace/DocumentWorkspace.tsx` | Единый сценарий (Explorer + Viewer + Remarks) |
| `ExplorerSidebar` | `src/components/workspace/ExplorerSidebar.tsx` | Дерево с onNodeClick callback |
| `RemarksPanel` | `src/components/RemarksPanel.tsx` | Замечания с documentId support |
| `DocumentCreate` | `src/pages/DocumentCreate.tsx` | Создание с выбором шаблона (3 шага) |
| `workspaceStore` | `src/components/workspace/store/workspaceStore.ts` | selectedDocument state |
| `viewer/types` | `src/components/viewers/types.ts` | supportsPreview, unsupported type |

---

## Пошаговая интеграция

### Шаг 1: Подключить DocumentWorkspace в роутинг

**Файл**: `src/App.tsx` (или `src/routes/index.tsx`)

```typescript
import DocumentWorkspace from './components/workspace/DocumentWorkspace';

// В роутере:
<Route path="/projects/:projectId/documents" element={<DocumentWorkspace />} />
// ИЛИ
<Route path="/documents/workspace/:projectId" element={<DocumentWorkspace />} />
```

**Заменить**:
- Убрать использование `DocumentDetail` для просмотра документов
- Перенаправить `/documents/:id` на workspace

### Шаг 2: Добавить API endpoint для замечаний по документу

**Backend**: `STDO/api/remarks.py` (или аналог)

```python
@router.get("/api/remarks/document/{document_id}")
async def get_remarks_by_document(
    document_id: int,
    status: Optional[RemarkStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Remark).filter(Remark.document_id == document_id)
    
    if status:
        query = query.filter(Remark.status == status)
    
    remarks = query.all()
    return remarks
```

**Frontend API**: Уже добавлено в `src/api/documents.ts`

```typescript
export const getRemarksByDocument = async (documentId: number): Promise<Remark[]> => {
  const { data } = await client.get(`/api/remarks/document/${documentId}`);
  return data;
};
```

### Шаг 3: Настроить file upload для revision

**Backend**: Добавить endpoint для загрузки файла ревизии

```python
@router.post("/api/documents/{document_id}/revisions/{revision_id}/upload")
async def upload_revision_file(
    document_id: int,
    revision_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Сохранить файл
    file_path = await save_file(file, f"documents/{document_id}/")
    
    # Обновить revision
    revision = db.query(Revision).get(revision_id)
    revision.file_path = file_path
    db.commit()
    
    return {"file_path": file_path}
```

**Frontend**: Добавить загрузку файла при создании ревизии

```typescript
// В DocumentDetail или DocumentWorkspace
const handleUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  await fetch(`/api/documents/${docId}/revisions/${revId}/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
};
```

### Шаг 4: Подключить реальные fileUrl из БД

**Изменить**: `DocumentWorkspace.tsx`

```typescript
// Сейчас:
const fileUrl = currentRevision?.file_path 
  ? `/api/files/${currentRevision.file_path}`
  : undefined;

// Убедиться, что backend возвращает полный URL или path
// Если backend возвращает full URL:
const fileUrl = currentRevision?.file_url || `/api/files/${currentRevision.file_path}`;
```

### Шаг 5: Тестирование

1. **Создать документ**:
   - Перейти на `/documents/new`
   - Выбрать категорию → шаблон → ввести детали
   - Убедиться, что документ создан и открыт

2. **Загрузить файл**:
   - Добавить ревизию с файлом
   - Убедиться, что файл загружен и file_path сохранен

3. **Открыть документ из дерева**:
   - Клик по документу в explorer
   - Убедиться, что viewer рендерит файл
   - Правая панель показывает замечания по document_id

4. **Проверить fallback для DWG**:
   - Загрузить .dwg файл
   - Убедиться, что показывается честный fallback UI

5. **Проверить масштабирование**:
   - PDF: zoom 0.5x, 1.0x, 2.0x, 3.0x
   - Изображение: fit to width, fit to page
   - Layout не ломается

---

## Структура states

```typescript
// Single source of truth
selectedDocument: {
  id: 1,
  code: 'НПЗ-КМ-001',
  title: 'Общий вид конструкций',
  fileUrl: '/api/files/path/to/file.pdf',
  fileName: 'НПЗ-КМ-001.pdf',
  project_id: 1,
  status: 'approved',
  doc_type: 'КМ',
  discipline: 'КМ'
}

// Viewer выводится из selectedDocument
viewerState = {
  fileUrl: selectedDocument.fileUrl,
  fileName: selectedDocument.fileName,
  fileType: detectType(selectedDocument.fileName), // 'pdf'
  isLoading: false,
  error: null
}

// Remarks привязаны к documentId
remarksState = {
  documentId: selectedDocument.id,
  remarks: [...],
  filter: 'all'
}
```

---

## Viewer Resolution Pipeline

```
1. detectType(fileName) → ViewerType
2. hasNativePreview(type) → boolean
3. Если supportsPreview:
   - Рендерить соответствующий Viewer (PDFViewer, ImageViewer, etc.)
   - Показать toolbar с Zoom/Pages/Download
4. Если !supportsPreview (DWG, unsupported):
   - Показать Fallback UI
   - Показать Download button
   - Предложить внешние решения (Autodesk Viewer, etc.)
```

---

## Файлы для проверки

### Созданы/Обновлены:

- [x] `src/components/workspace/DocumentWorkspace.tsx`
- [x] `src/components/workspace/types/workspace.types.ts`
- [x] `src/components/workspace/store/workspaceStore.ts`
- [x] `src/components/viewers/types.ts`
- [x] `src/components/viewers/ViewerContainer.tsx` (уже есть)
- [x] `src/components/viewers/DWGViewer.tsx` (уже есть)
- [x] `src/components/RemarksPanel.tsx`
- [x] `src/components/workspace/ExplorerSidebar.tsx`
- [x] `src/api/documents.ts`
- [x] `src/pages/DocumentCreate.tsx`

### Требуют доработки:

- [ ] `src/App.tsx` — подключить DocumentWorkspace
- [ ] Backend API `/api/remarks/document/:id`
- [ ] Backend API `/api/files/:path`
- [ ] Backend API upload revision file
- [ ] Добавить реальные данные вместо моков

---

## Acceptance Criteria (чеклист)

### Viewer

- [ ] PDF открывается и рендерится
- [ ] Zoom 0.5x - 3.0x работает
- [ ] Навигация по страницам работает
- [ ] Изображения fit/zoom корректны
- [ ] Excel листы переключаются
- [ ] Word показывает текст
- [ ] DWG показывает fallback с кнопками
- [ ] Неподдерживаемый формат → fallback
- [ ] Loading spinner + текст
- [ ] Error state + действие

### Навигация

- [ ] Active state в дереве
- [ ] Viewer обновляется при клике
- [ ] Remarks привязаны к document_id
- [ ] Повторный клик → no-op
- [ ] Клик по папке → expand only
- [ ] Закрытие таба → prev tab или empty

### Layout

- [ ] Zoom не ломает layout
- [ ] Нет двойных scroll
- [ ] Sidebar ресайз работает
- [ ] Collapsed sidebar → центр расширяется
- [ ] Window resize → viewer fit

### Создание

- [ ] Выбор шаблона только при создании
- [ ] Flow: категория → шаблон → детали
- [ ] После создания → открытие в центре
- [ ] Шаблон предзаполняет поля

---

## Next Steps

1. **Создать API endpoints** (backend)
2. **Подключить DocumentWorkspace** (frontend routing)
3. **Настроить upload** (file upload flow)
4. **Протестировать** (см. acceptance criteria)
5. **Deploy** (staging → production)

---

## Контакты

Вопросы по реализации:
- Frontend: проверить `STDO/frontend/src/components/workspace/DocumentWorkspace.tsx`
- Backend: добавить endpoints для remarks/document и file upload
- UX: см. `STDO/frontend/docs/DOCUMENT_WORKSPACE_UX_SPEC.md`
