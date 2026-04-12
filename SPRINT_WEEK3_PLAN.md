# План Недели 3 (P2-P3): Качество, DX, Архитектура

**Дата**: 2026-01-22  
**Цель**: Улучшение качества кода, DX (Developer Experience), снижение техдолга

---

## Текущее состояние

### Покрытие тестами

**Unit тесты**: ✅ 278 тестов  
**Интеграционные тесты**: ✅ 20+ тестов  
**E2E тесты**: ⚠️ Требуют `requests` (не установлен)

### Выявленные проблемы

| Категория | Проблема | Приоритет |
|-----------|----------|-----------|
| **DX** | Нет pre-commit hooks для линтинга | P2 |
| **DX** | Нет автоматического форматирования кода | P2 |
| **Архитектура** | BaseRepository существует, но не используется всеми | P2 |
| **Техдолг** | Нет документации по API endpoints | P2 |
| **Мониторинг** | Нет health check endpoint | P2 |
| **Мониторинг** | Нет метрик производительности | P2 |
| **DX** | Нет автоматической генерации OpenAPI схемы | P2 |
| **Тесты** | Нет coverage report | P3 |
| **Техдолг** | Нет README для модулей | P3 |
| **Архитектура** | Нет единого места для констант | P3 |

---

## Приоритетные задачи P2

### P2.1: Pre-commit Hooks и Автоматический Линтинг

**Цель**: Автоматическое форматирование и проверка кода перед коммитом

**Файлы**:
- `.pre-commit-config.yaml` (существует, но не активирован)
- `pyproject.toml` (ruff/black конфигурация)

**Что сделать**:
1. Установить pre-commit hooks
2. Настроить ruff для линтинга
3. Настроить black для форматирования
4. Добавить hooks к `.gitignore`

**Эффект**:
- Единый стиль кода
- Автоматические исправления
- Меньше code review замечаний

---

### P2.2: Health Check Endpoint

**Цель**: Добавить endpoint для мониторинга состояния приложения

**Файлы**:
- `api/health_api.py` (новый)
- `main.py` (добавить router)

**Endpoints**:
```
GET /api/health - Базовый health check
GET /api/health/db - Проверка подключения к БД
GET /api/health/redis - Проверка Redis (если есть)
GET /api/health/metrics - Метрики приложения
```

**Эффект**:
- Kubernetes readiness/liveness probes
- Мониторинг в production
- Быстрая диагностика проблем

---

### P2.3: OpenAPI Documentation

**Цель**: Автоматическая генерация и публикация API документации

**Файлы**:
- `docs/API_REFERENCE.md` (новый)
- `main.py` (добавить OpenAPI metadata)

**Что сделать**:
1. Добавить `@router.get(..., summary="...", description="...")` ко всем endpoints
2. Настроить FastAPI для генерации `openapi.json`
3. Добавить Swagger UI / ReDoc
4. Экспорт документации в Markdown

**Эффект**:
- Автодокументация для frontend команды
- Тестирование API через Swagger UI
- Актуальная документация всегда

---

### P2.4: Метрики Производительности

**Цель**: Добавить сбор метрик для мониторинга

**Файлы**:
- `core/metrics.py` (новый)
- `api/metrics_api.py` (новый)

**Метрики**:
- Время ответа API endpoints
- Количество запросов к БД
- Кэш хитрейт (если Redis)
- Ошибки и исключения

**Эффект**:
- Prometheus/Grafana интеграция
- Обнаружение деградации производительности
- Capacity planning

---

### P2.5: Унификация Repository Pattern

**Цель**: Использовать BaseRepository везде для снижения дублирования

**Файлы**:
- Все `repositories/*.py`

**Что сделать**:
1. Проверить какие repository наследуются от BaseRepository
2. Переписать оставшиеся на BaseRepository
3. Удалить дублирующийся CRUD код

**Эффект**:
- Меньше кода (DRY)
- Единый стиль
- Меньше багов

---

### P2.6: Константы и Enums

**Цель**: Вынести константы в единый модуль

**Файлы**:
- `constants.py` (новый)
- `models/enums.py` (существует)

**Константы**:
- Статусы (ProjectStatus, DocumentStatus, TaskStatus)
- Роли пользователей
- Константы бизнес-логики
- Системные константы

**Эффект**:
- Нет магических строк
- Единый источник правды
- Автодокументация

---

## Приоритетные задачи P3

### P3.1: Coverage Report

**Цель**: Генерация отчета покрытия тестами

**Файлы**:
- `pyproject.toml` (добавить coverage config)
- `.github/workflows/ci.yml` (добавить coverage step)

**Что сделать**:
1. Добавить `pytest-cov` в dev dependencies
2. Настроить `.coveragerc`
3. Добавить badge в README
4. Генерация HTML report

**Эффект**:
- Видно какие части кода не покрыты
- Target coverage (например, 80%)
- Улучшение качества тестов

---

### P3.2: Модульная Документация

**Цель**: README для каждого модуля

**Файлы**:
- `services/README.md`
- `repositories/README.md`
- `api/README.md`
- `core/README.md`

**Что включить**:
- Описание модуля
- Основные классы/функции
- Примеры использования
- Зависимости

**Эффект**:
- Быстрое онбординг новых разработчиков
- Понятная архитектура
- Меньше вопросов в чате

---

### P3.3: Улучшение Error Handling

**Цель**: Единая система обработки ошибок

**Файлы**:
- `core/exceptions.py` (новый)
- `main.py` (добавить exception handlers)

**Что сделать**:
1. Определить кастомные исключения
2. Добавить глобальный exception handler
3. Логирование ошибок с контекстом
4. Единый формат ошибок в API

**Эффект**:
- Понятные ошибки для клиентов
- Лучше логирование
- Проще отладка

---

### P3.4: Database Migration Best Practices

**Цель**: Улучшить процесс миграций

**Файлы**:
- `alembic.ini`
- `alembic/`

**Что сделать**:
1. Настроить Alembic для automatic migrations
2. Добавить rollback scripts
3. Добавить migration testing
4. Документация по миграциям

**Эффект**:
- Безопасные миграции
- Легкий rollback
- Автоматическое тестирование

---

### P3.5: Integration Test Coverage

**Цель**: Увеличить покрытие интеграционных тестов

**Файлы**:
- `tests/test_integration.py`

**Что покрыть**:
- Document workflow (создание → ревизия → утверждение)
- Project lifecycle (tender → project → tasks → completion)
- Gamification flow (events → score → badges)

**Эффект**:
- Проверка реальной работы системы
- Обнаружение интеграционных багов
- Уверенность при рефакторинге

---

## План на неделю (итеративный)

### День 1: DX Improvements (P2.1, P2.3)

```bash
# Установить pre-commit hooks
pip install pre-commit black ruff
pre-commit install

# Настроить API documentation
# Добавить summary/description ко всем endpoints
# Включить Swagger UI
```

**Deliverables**:
- ✅ Pre-commit hooks работают
- ✅ Swagger UI доступен
- ✅ OpenAPI schema экспортируется

---

### День 2: Health Check & Metrics (P2.2, P2.4)

```python
# Создать health_api.py
# Добавить metrics collection
# Интегрировать в main.py
```

**Deliverables**:
- ✅ `/api/health` endpoint
- ✅ `/api/health/db` endpoint
- ✅ `/api/metrics` endpoint

---

### День 3: Repository Refactoring (P2.5)

```python
# Проверить все repositories
# Переписать на BaseRepository
# Удалить дублирование
```

**Deliverables**:
- ✅ Все repositories используют BaseRepository
- ✅ Меньше кода на 15-20%
- ✅ Все тесты проходят

---

### День 4: Constants & Error Handling (P2.6, P3.3)

```python
# Создать constants.py
# Создать core/exceptions.py
# Обновить все модули
```

**Deliverables**:
- ✅ Единый constants модуль
- ✅ Кастомные исключения
- ✅ Глобальный error handler

---

### День 5: Documentation & Cleanup (P3.2, P3.4)

```markdown
# Написать модульные README
# Документировать миграции
# Очистить код
```

**Deliverables**:
- ✅ README для всех модулей
- ✅ Migration guide
- ✅ Code cleanup

---

## Метрики успеха

| Метрика | До | После | Target |
|---------|-----|-------|--------|
| **Pre-commit hooks** | Нет | ✅ | 100% |
| **API Documentation** | Частично | Swagger | 100% |
| **Health Check** | Нет | 3 endpoints | ✅ |
| **Repository DRY** | 50% | 100% | ✅ |
| **Coverage** | N/A | 70%+ | 70% |
| **Module README** | 0 | 4+ | 100% |
| **Error Handling** | Разрозненное | Единое | ✅ |

---

## Риски

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Pre-commit замедляет разработку | Низкая | Настроить async hooks |
| BaseRepository ломает существующий код | Средняя | Полное тестирование |
| Metrics overhead | Низкая | Отключаемый collection |
| Documentation устаревает | Средняя | Auto-generate из docstrings |

---

## Заключение

Неделя 3 фокусируется на **долгосрочном качестве** проекта, а не на срочных исправлениях. Все задачи безопасны, обратимы и приносят измеримую пользу DX и поддерживаемости кода.

**Ожидаемый результат**:
- ✅ Единый стиль кода (pre-commit)
- ✅ Автодокументация API (Swagger)
- ✅ Мониторинг (health + metrics)
- ✅ Уменьшение дублирования (BaseRepository)
- ✅ Лучшие ошибки (exceptions)
- ✅ Полная документация (README)
