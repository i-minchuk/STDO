# Дизайн-Система DokPotok IRIS

## 1. Цветовая Палитра

### Семантические Токены (Единый источник правды)

Все цвета в проекте используются **только через семантические токены**. Для изменения палитры редактируйте `:root` в `index.css`.

#### Фоны
```
--bg-page:   #F8FAFC  (фон страницы)
--bg-card:   #FFFFFF  (фон карточек, панелей)
```

#### Текст
```
--text-base:    #0F172A  (основной текст)
--text-muted:   #64748B  (вторичный текст)
```

#### Primary (Фиолетовый)
```
--primary:       #7C3AED  (базовый)
--primary-hover: #6D28D9  (ховер)
--primary-light: #A78BFA  (светлый акцент)
```

#### Secondary (Slate)
```
--secondary: #334155  (нейтральный темный)
```

#### Семантические цвета
```
--success: #4ADE80  (успех, утверждено)
--warning: #D97706  (предупреждение, проверка)
--error:   #DC2626  (ошибка, отклонено, просрочено)
--info:    #0F766E  (информация, в работе)
```

#### Границы
```
--border:       #CBD5E1  (основная граница)
--border-light: #E2E8F0  (легкая граница)
```

#### Ghost состояния
```
--ghost-bg:    transparent  (фон)
--ghost-text:  #475569      (текст)
--ghost-hover: #F1F5F9      (ховер фон)
```

### Status Badges
```
Green (success):  Approved, Completed, Low Priority
Yellow (warning): On Review, In Progress, Medium Priority
Red (error):      Error, Overdue, High Priority
Blue (info):      Active, In Progress
Gray (secondary): Draft, Archived, Not Started
```

---

## Правила Использования Цветов

### ⚠️ ЗАПРЕЩЕНО
- Прямые HEX-цвета в компонентах (`#3b82f6`, `#ef4444`, и т.д.)
- Стандартные Tailwind цвета без семантики (`bg-red-500`, `text-green-600`)

### ✅ РАЗРЕШЕНО
- CSS-переменные: `var(--primary)`, `var(--bg-card)`
- Семантические классы Tailwind: `bg-primary`, `text-success-700`
- Осветленные варианты для фонов: `bg-success-50`, `bg-error-50`

---

## 2. Типографика

### Шрифты
```
Primary: 'Inter', system-ui, sans-serif
Mono:    'Fira Code', 'Courier New', monospace (для кодов документов)
```

### Размеры текста
```
Text-xs:  0.75rem (12px)  - мета-данные, подписи
Text-sm:  0.875rem (14px) - вторичный текст
Text-base: 1rem    (16px) - основной текст
Text-lg:  1.125rem (18px) - заголовки разделов
Text-xl:  1.25rem (20px)  - подзаголовки
Text-2xl: 1.5rem  (24px)  - заголовки страниц
Text-3xl: 1.875rem (30px) - основные заголовки
```

### Жирность
```
Font-normal: 400 - основной текст
Font-medium: 500 - акцентный текст
Font-semibold: 600 - заголовки
Font-bold: 700 - основные заголовки
```

### Высота строки
```
Leading-tight: 1.25 - заголовки
Leading-snug:  1.375 - подзаголовки
Leading-normal: 1.5 - основной текст
Leading-relaxed: 1.625 - длинные тексты
```

## 3. Spacing (Отступы)

### Base Unit: 4px
```
Space-0:   0px
Space-1:   0.25rem (4px)   - микро-отступы
Space-2:   0.5rem  (8px)   - отступы внутри элементов
Space-3:   0.75rem (12px)  - отступы между related элементами
Space-4:   1rem    (16px)  - базовый отступ
Space-5:   1.25rem (20px)
Space-6:   1.5rem  (24px)  - отступы между секциями
Space-8:   2rem    (32px)
Space-10:  2.5rem  (40px)
Space-12:  3rem    (48px)
```

### Карточки и контейнеры
```
Card padding: p-6 (24px)
Card small:   p-3 (12px)
Card large:   p-8 (32px)
```

### Таблицы
```
Cell padding: px-6 py-4 (24px horizontal, 16px vertical)
Header padding: px-6 py-3
```

## 4. Компоненты

### Button

#### Variants
```typescript
primary:  'bg-primary text-white hover:bg-primary-hover'
secondary: 'bg-bg-card text-secondary border border-border hover:bg-ghost-hover'
outline:  'border border-border bg-transparent hover:bg-ghost-hover text-text-base'
ghost:    'bg-ghost-bg hover:bg-ghost-hover text-ghost-text'
danger:   'bg-error text-white hover:bg-error-700'
success:  'bg-success text-text-base hover:bg-success-700'
```

#### Sizes
```typescript
sm: 'px-3 py-1.5 text-xs'       // ~32px height
md: 'px-4 py-2 text-sm'         // ~38px height
lg: 'px-6 py-3 text-base'       // ~48px height
```

#### States
```typescript
default: shadow-sm
hover:   shadow-md
active:  active:scale-95
disabled: opacity-50 pointer-events-none
loading:  spinner + disabled
```

### Card

```typescript
base: 'bg-bg-card rounded-xl shadow-sm border border-border-light'
padding: 'p-6' | 'p-3' | 'p-8' | ''
hover: 'hover:shadow-md transition-shadow'
```

### Input

```typescript
base: 'block w-full rounded-lg border-border shadow-sm focus:border-primary focus:ring-primary'
sizes: 'h-10' (40px) | 'h-9' (36px)
states:
  default: border-border
  focus:   border-primary ring-2 ring-primary-100
  error:   border-error focus:border-error focus:ring-error-100
  disabled: bg-bg-page cursor-not-allowed
```

### Badge

```typescript
variants:
  gray:   'bg-secondary-100 text-secondary-700 border-secondary-200'
  blue:   'bg-info-100 text-info-700 border-info-200'
  green:  'bg-success-100 text-success-700 border-success-200'
  yellow: 'bg-warning-100 text-warning-700 border-warning-200'
  red:    'bg-error-100 text-error-700 border-error-200'
  indigo: 'bg-primary-100 text-primary-700 border-primary-200'

sizes: 'px-2.5 py-0.5 text-xs font-medium rounded-full border'
```

### Table

```typescript
base: 'min-w-full divide-y divide-border-light'
header: 'bg-bg-page text-xs font-bold text-text-muted uppercase'
cell: 'px-6 py-4 whitespace-nowrap text-sm'
row: 'hover:bg-bg-page transition-colors'
```

## 5. Layout

### Grid System
```typescript
Container max-width: 1280px
Gaps:
  gap-4:  1rem (16px)  - базовый
  gap-6:  1.5rem (24px) - между секциями
  gap-8:  2rem (32px)   - между страницами

Grid columns:
  grid-cols-1     - mobile
  sm:grid-cols-2  - tablet
  lg:grid-cols-3  - desktop
  xl:grid-cols-4  - large screens
```

### Breakpoints
```css
sm:  640px   (tablet portrait)
md:  768px   (tablet landscape)
lg:  1024px  (desktop)
xl:  1280px  (large desktop)
2xl: 1536px  (extra large)
```

## 6. States & Interactions

### Hover
```css
transition-all duration-200
hover:scale-105 (только для карточек)
hover:shadow-md
hover:bg-gray-50 (для строк таблиц)
```

### Focus
```css
focus:outline-none
focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
```

### Active
```css
active:scale-95
active:bg-gray-100
```

### Loading
```css
animate-pulse (для skeleton)
animate-spin (для spinner)
```

### Transitions
```css
default: transition-all duration-200 ease-in-out
fast:    transition-all duration-150
slow:    transition-all duration-300
```

## 7. Примеры Использования

### Кнопка
```tsx
<Button 
  variant="primary" 
  size="md" 
  isLoading={loading}
  onClick={handleSubmit}
>
  Сохранить документ
</Button>
```

### Карточка
```tsx
<Card padding="md" className="hover:shadow-md">
  <h3 className="text-text-base font-semibold mb-2">Название</h3>
  <p className="text-text-muted">Описание</p>
</Card>
```

### Инпут
```tsx
<Input
  label="Код документа"
  placeholder="Например: НПЗ-КМ-001"
  value={code}
  onChange={setCode}
  error={errors.code}
/>
```

### Таблица
```tsx
<Card padding="none">
  <table className="min-w-full divide-y divide-border-light">
    <thead className="bg-bg-page">
      <tr>
        <th className="px-6 py-3 text-left text-xs font-bold text-text-muted uppercase">
          Код
        </th>
      </tr>
    </thead>
    <tbody className="bg-bg-card divide-y divide-border-light">
      {docs.map(doc => (
        <tr key={doc.id} className="hover:bg-bg-page">
          <td className="px-6 py-4 text-sm text-text-base">{doc.code}</td>
        </tr>
      ))}
    </tbody>
  </table>
</Card>
```

### Алерты
```tsx
<div className="p-4 bg-success-50 border border-success rounded-lg">
  <p className="text-text-base font-medium">Успешно!</p>
  <p className="text-text-muted text-sm mt-1">Документ сохранён</p>
</div>

<div className="p-4 bg-error-50 border border-error rounded-lg">
  <p className="text-text-base font-medium">Ошибка</p>
  <p className="text-text-muted text-sm mt-1">Не удалось сохранить</p>
</div>
```

---

## 8. Тестирование Цветовой Схемы

Для проверки всех компонентов откройте страницу `/color-test`:

```bash
cd STDO/frontend
npm run dev
# Откройте http://localhost:5173/color-test
```

На странице представлены:
- Все варианты кнопок
- Бейджи всех цветов
- Статусы (StatusBadge)
- Алерты/баннеры
- Карточки с текстом
- Цветовые образцы
- Формы с состояниями

## 9. Доступность (A11y)

### Контрастность
- Текст на белом: min 4.5:1 (text-text-base, text-muted)
- Крупный текст: min 3:1
- Интерактивные элементы: min 3:1
- **Success (#4ADE80)**: использовать с text-text-base для контраста

### Клавиатура
- Все интерактивные элементы доступны с Tab
- Focus visible: ring-2 ring-primary
- Skip to main content link

### ARIA
- Labels для всех инпутов
- Roles для навигации
- Live regions для уведомлений

---

**Версия**: 2.0.0 (Semantic Colors)
**Последнее обновление**: 2025-01-XX
**Изменения**: Полная миграция на семантические цветовые токены
