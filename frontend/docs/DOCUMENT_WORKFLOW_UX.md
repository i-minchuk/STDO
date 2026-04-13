# UX Карта: Документный Флоу

## 1. Пользовательский Сценарий (Happy Path)

### Шаг 1: Создание Проекта
**Цель**: Создать новый проект для документов

**Экран**: `/projects/new` (или через `/dashboard`)

**Действия пользователя**:
1. Нажать "Создать проект"
2. Заполнить форму:
   - Код проекта (например: "НПЗ-2026")
   - Название проекта
   - Заказчик
   - Дата начала
3. Нажать "Создать"

**API**: `POST /api/projects`

**Состояния**:
- Loading: skeleton экрана
- Success: редирект на экран проекта
- Error: показать сообщение об ошибке

---

### Шаг 2: Создание Документа
**Цель**: Создать новый документ в проекте

**Экран**: `/documents/new` или `/projects/:projectId/documents/new`

**Действия пользователя**:
1. Выбрать проект (если не выбран)
2. Заполнить форму:
   - Код документа (например: "НПЗ-КМ-001")
   - Название
   - Дисциплина (КМ, ЭС, АР и т.д.)
   - Тип документа
3. Нажать "Создать документ"

**API**: `POST /api/documents`

**Состояния**:
- Loading: skeleton формы
- Success: редирект на экран документа
- Error: показать сообщение об ошибке

---

### Шаг 3: Создание Ревизии
**Цель**: Создать первую ревизию документа

**Экран**: `/documents/:id` (таб "Ревизии")

**Действия пользователя**:
1. Нажать "Создать ревизию"
2. Заполнить форму:
   - Индекс ревизии (A.1, B.1 и т.д.)
   - Описание изменений
   - Загрузить файл (PDF/DWG)
3. Нажать "Создать"

**API**: `POST /api/documents/:id/revisions`

**Состояния**:
- Loading: skeleton модального окна
- Success: обновить таблицу ревизий
- Error: показать сообщение об ошибке

---

### Шаг 4: Утверждение Ревизии
**Цель**: Утвердить ревизию документа

**Экран**: `/documents/:id` (таб "Ревизии")

**Действия пользователя**:
1. Найти ревизию в таблице
2. Нажать "Утвердить" (кнопка в строке)
3. Подтвердить действие (опционально)

**API**: `POST /api/documents/:id/revisions/:revisionId/approve`

**Состояния**:
- Loading: spinner на кнопке
- Success: обновить статус (желтый → зеленый)
- Error: показать сообщение об ошибке

---

### Шаг 5: Просмотр Актуального Состояния
**Цель**: Убедиться, что документ утверждён

**Экран**: `/documents/:id` (таб "Обзор")

**Действия пользователя**:
1. Открыть документ
2. Проверить статус (должен быть "Утверждён")
3. Проверить текущую ревизию (должна быть утверждённая)

**API**: `GET /api/documents/:id`

**Состояния**:
- Success: показать актуальные данные
- Error: показать сообщение об ошибке

---

## 2. Экраны и Компоненты

### 2.1. Список Проектов

**Маршрут**: `/projects`

**Компоненты**:
- Header: "Проекты" + "Создать проект"
- Фильтры: поиск, статус, заказчик
- Таблица проектов
- Пагинация

**API**:
- `GET /api/projects` - список
- `GET /api/projects/:id` - детали

---

### 2.2. Экран Проекта

**Маршрут**: `/projects/:id`

**Компоненты**:
- Header: код проекта + статус
- Карточка проекта (заказчик, даты, бюджет)
- Таблица документов проекта
- Статистика (всего документов, на проверке, утверждено)

**API**:
- `GET /api/projects/:id` - проект
- `GET /api/projects/:id/documents` - документы проекта

---

### 2.3. Список Документов

**Маршрут**: `/documents`

**Компоненты**:
- Header: "Документы" + "Добавить документ"
- Фильтры: поиск, статус, дисциплина
- Таблица документов
- Пагинация
- Bulk actions (выделение)

**API**:
- `GET /api/documents` - все документы
- `GET /api/documents?project_id=:id` - документы проекта

---

### 2.4. Экран Документа

**Маршрут**: `/documents/:id`

**Компоненты**:
- Header: код документа + статус + badge
- Карточка документа (название, дисциплина, создатель)
- Tabs:
  1. **Обзор** - краткая информация
  2. **Ревизии** - таблица всех ревизий
  3. **Задачи** - связанные задачи
  4. **Журнал** - аудит лог

**API**:
- `GET /api/documents/:id` - документ с ревизиями

---

### 2.5. Форма Создания Документа

**Маршрут**: `/documents/new`

**Компоненты**:
- Modal или отдельная страница
- Форма:
  - Project (select)
  - Code (text, required, unique validation)
  - Title (text, required)
  - Discipline (select)
  - Doc type (select)
- Кнопки: "Создать", "Отмена"

**API**:
- `GET /api/projects` - для select проекта
- `POST /api/documents` - создание

---

### 2.6. Форма Создания Ревизии

**Маршрут**: `/documents/:id/revisions/new` (modal)

**Компоненты**:
- Modal
- Форма:
  - Revision index (text, pattern: [A-Z]\.\d+)
  - Revision letter (select: A, B, C...)
  - Revision number (number)
  - Change log (textarea)
  - File upload (drag & drop)
- Кнопки: "Создать", "Отмена"

**API**:
- `POST /api/documents/:id/revisions` - создание

---

## 3. Состояния Экранных Компонентов

### Loading States
```tsx
// Skeleton для карточки
<Card className="animate-pulse">
  <div className="h-8 bg-gray-200 rounded mb-4 w-3/4"></div>
  <div className="h-4 bg-gray-200 rounded mb-2"></div>
  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
</Card>

// Skeleton для строки таблицы
<tr>
  <td><div className="h-4 bg-gray-100 rounded w-24" /></td>
  <td><div className="h-4 bg-gray-100 rounded w-48" /></td>
</tr>
```

### Empty States
```tsx
// Нет документов
<div className="py-12 text-center text-gray-400">
  <FileText size={32} className="mx-auto mb-2" />
  <p>Документы не найдены</p>
  <Button variant="ghost">Добавить документ</Button>
</div>

// Нет ревизий
<div className="py-12 text-center text-gray-400">
  <GitFork size={32} className="mx-auto mb-2" />
  <p>Ревизии не созданы</p>
  <Button variant="ghost">Создать первую ревизию</Button>
</div>
```

### Error States
```tsx
// Ошибка API
<Card className="bg-red-50 border-red-200">
  <div className="flex items-center gap-2 text-red-700">
    <AlertCircle size={20} />
    <p>Ошибка загрузки данных. Попробуйте обновить страницу.</p>
  </div>
</Card>

// Ошибка валидации формы
<Input
  label="Код"
  value={code}
  error="Документ с таким кодом уже существует"
/>
```

---

## 4. Интеграция с API

### API Endpoints для Документного Флоу

| Экран | Метод | Endpoint | Описание |
|-------|-------|----------|----------|
| Список документов | GET | `/api/documents` | Все документы |
| Детали документа | GET | `/api/documents/:id` | Документ + ревизии |
| Создать документ | POST | `/api/documents` | Новый документ |
| Список ревизий | GET | `/api/documents/:id/revisions` | Ревизии документа |
| Создать ревизию | POST | `/api/documents/:id/revisions` | Новая ревизия |
| Утвердить ревизию | POST | `/api/documents/:id/revisions/:revId/approve` | Approval |
| Скачать файл | GET | `/api/documents/:id/revisions/:revId/file` | Download |

### Auth Flow
```
1. POST /api/auth/login → { access_token, refresh_token }
2. Сохранить token в localStorage
3. Добавить Authorization header к каждому запросу
4. При 401 → редирект на /login
```

---

## 5. Accessibility Checklist

- [ ] Все инпуты имеют label
- [ ] Кнопки имеют aria-label (если нет текста)
- [ ] Focus visible для всех интерактивных элементов
- [ ] Tab порядок логичный
- [ ] ARIA live regions для уведомлений
- [ ] Контрастность текста ≥ 4.5:1
- [ ] Поддержка клавиатуры (Enter, Escape)
- [ ] Skip to main content link

---

## 6. Future Enhancements

### Phase 2 (следующий спринт)
- [ ] Drag & drop загрузка файлов
- [ ] Preview PDF в браузере
- [ ] Commenting на ревизиях
- [ ] Notification system
- [ ] Export документов в Excel

### Phase 3
- [ ] Bulk operations (mass approve, mass archive)
- [ ] Document comparison (diff ревизий)
- [ ] Version history visualization
- [ ] Mobile responsive improvements

---

**Версия**: 1.0.0
**Последнее обновление**: 2025-06-15
