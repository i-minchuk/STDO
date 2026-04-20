# ДокПоток IRIS — Инструкции для AI-ассистента

## Обзор проекта

**ДокПоток IRIS** — это система управления инженерной документацией для инженерных, EPC и проектных команд. Продукт помогает отслеживать ревизии документов, сроки выпуска, процессы согласования и исполнительскую дисциплину в едином рабочем контуре.

Проект состоит из двух частей:

- **Лендинг** (`stdo-landing.html`) — статическая HTML-страница для демонстрации продукта потенциальным клиентам
- **Приложение** (`STDO/`) — полноценное веб-приложение с backend на Python и frontend на TypeScript

---

## Тип проекта

Это **программный проект** с backend и frontend частями.

### Стек технологий

#### Backend
- **Python 3.12+**
- **FastAPI** — веб-фреймворк
- **PostgreSQL 15** — база данных (через psycopg 3)
- **Pydantic v2** — валидация данных и DTO
- **Alembic** — миграции базы данных

#### Frontend
- **TypeScript**
- **Vite** — сборщик
- **Tailwind CSS** — стилизация

#### Инфраструктура
- **Docker / Docker Compose** — контейнеризация
- **GitHub Actions** — CI/CD

---

## Структура директорий

```
.
├── KODA.md                     # Этот файл
├── stdo-landing.html           # Лендинг продукта
├── GEMINI.md                   # Скилл для AI-агента (продуктовый Python-архитектор)
├── варианты названий.txt       # (пустой файл)
└── STDO/                       # Основное приложение
    ├── main.py                 # Точка входа FastAPI-приложения
    ├── config.py               # Конфигурация приложения
    ├── api/                    # Обработчики маршрутов FastAPI
    ├── core/                   # Service locator (DI-контейнер)
    ├── db/                     # Подключение к БД и миграции
    ├── dto/                    # Pydantic DTO (схемы запросов/ответов)
    ├── models/                 # Доменные модели (dataclasses)
    ├── repositories/           # Слой доступа к данным (SQL-запросы через psycopg)
    ├── services/               # Бизнес-логика
    ├── frontend/               # Frontend-приложение
    │   ├── src/                # Исходный код TypeScript
    │   ├── package.json        # Зависимости npm
    │   └── vite.config.ts      # Конфигурация Vite
    ├── tests/                  # Тесты
    ├── scripts/                # Скрипты для разработки
    ├── docs/                   # Документация
    ├── alembic/                # Миграции Alembic
    ├── pyproject.toml          # Конфигурация проекта Python
    ├── requirements.txt        # Зависимости Python
    ├── requirements-dev.txt    # Зависимости для разработки
    ├── docker-compose.yml      # Docker Compose для запуска
    ├── .env.example            # Пример переменных окружения
    └── README.md               # Документация проекта
```

---

## Сборка и запуск

### Предварительные требования

- Python 3.12+
- Node.js 20+ (для frontend)
- PostgreSQL 15
- Docker и Docker Compose (опционально)
- Conda (опционально, для управления Python-окружением)

### Быстрый старт (с Docker)

```bash
cd STDO
docker compose up -d
```

Приложение будет доступно по адресу: http://localhost:8000

### Быстрый старт (без Docker)

#### 1. Запуск базы данных

```bash
cd STDO
docker compose up -d postgres
```

#### 2. Установка зависимостей

**Вариант A: virtualenv**

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Вариант B: Conda**

```bash
conda env create -f environment.yml
conda activate iris
# Linux/Mac
./scripts/setup_dev.sh
# Windows PowerShell
scripts\setup_dev.ps1
```

#### 3. Установка зависимостей frontend

```bash
cd frontend
npm ci
```

#### 4. Настройка переменных окружения

```bash
# Linux/Mac
cp .env.example .env
# Windows PowerShell
Copy-Item .env.example .env
```

#### 5. Запуск миграций базы данных

```bash
python -m db.migrations_runner
```

#### 6. Запуск сервера

```bash
uvicorn main:app --reload
```

API документация будет доступна по адресу: http://localhost:8000/docs

#### 7. (Опционально) Загрузка тестовых данных

```bash
python -m project.scripts.init_sample_project
```

### Запуск с использованием VS Code Dev Container

1. Откройте проект в VS Code
2. Выберите "Reopen in Container" из командной палитры
3. Dev Container автоматически установит зависимости и запустит серверы

### Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `IRIS_DB_DSN` | `postgresql://postgres:Qwerty852@localhost:5432/iris` | Строка подключения к PostgreSQL |
| `IRIS_STORAGE_ROOT` | `./storage` | Директория для хранения файлов ревизий |
| `IRIS_SECRET_KEY` | `iris-secret-key-change-in-production` | Секретный ключ для JWT-аутентификации |
| `IRIS_LOG_LEVEL` | `INFO` | Уровень логирования |
| `TEST_DB_DSN` | `postgresql://postgres:Qwerty852@localhost:5432/iris_test` | DSN для интеграционных тестов |

---

## Тестирование

### Запуск всех тестов

```bash
pytest tests/ -v
```

### Запуск интеграционных тестов

Интеграционные тесты требуют реальную базу данных PostgreSQL:

```bash
# Linux/Mac
export TEST_DB_DSN="postgresql://postgres:Qwerty852@localhost:5432/iris_test"
pytest -m integration -q

# Windows PowerShell
$env:TEST_DB_DSN = "postgresql://postgres:Qwerty852@localhost:5432/iris_test"
pytest -m integration -q
```

### Запуск только юнит-тестов

```bash
pytest -m "not integration" -v
```

---

## Линтинг и форматирование

### Python

```bash
pip install -r requirements-dev.txt
python -m ruff check .
python -m black --check .
python -m pre_commit install
python -m pre_commit run --all-files
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

---

## Архитектура приложения

```
api/           Обработчики маршрутов FastAPI
core/          Service locator (DI-контейнер)
db/            Подключение к БД и миграции
dto/           Pydantic DTO (схемы запросов/ответов API)
models/        Доменные модели (dataclasses)
repositories/  Слой доступа к данным (SQL-запросы через psycopg)
services/      Бизнес-логика
```

### Основные API-эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/projects/` | Список всех проектов |
| GET | `/api/projects/portfolio/today` | Обзор портфеля проектов |
| POST | `/api/documents/{id}/revisions` | Создание ревизии с загрузкой файла |
| POST | `/api/revisions/{id}/approve` | Одобрение ревизии |
| POST | `/api/internal/projects/{id}/recalc_cpm_and_metrics` | Пересчёт графика CPM и метрик |
| GET | `/health` | Проверка здоровья сервиса |

---

## Основные функциональные возможности

1. **Управление документами** — создание документов, отслеживание ревизий (A01, A02, B01...), процессы согласования
2. **Планирование проектов** — CPM-метод (Critical Path Method) с прямым и обратным проходом
3. **Управление задачами** — инженерные задачи, задачи на проверку и согласование с зависимостями
4. **Дашборд портфеля** — обзор всех проектов, метрики SPI/CPI, уровни риска
5.Геймификация — метрики инженеров, очки, отслеживание XP

---

## Правила разработки

### Стиль кода Python

- **Black** — форматирование (длина строки 88 символов)
- **Ruff** — линтинг
- **Pydantic v2** — для всех DTO и моделей данных
- Следовать существующей архитектуре: API → Services → Repositories

### Стиль кода TypeScript

- ESLint для линтинга
- Vite для сборки
- Tailwind CSS для стилизации

### Общие правила

- Все изменения должны сохранять обратную совместимость API
- Минимальные изменения — исправлять только конкретную проблему
- Не переписывать существующий код без явной необходимости
- Использовать существующие helpers и services
- Соблюдать границы слоёв: handlers не должны содержать бизнес-логику, services не должны обходить repositories без причины

---

## Доступные скиллы для AI-агента

В проекте определён скилл для AI-агента, ориентированный на продуктовую разработку на Python:

- **product-python-architect** — используется для продуктового мышления, уточнения требований, планирования фич, проектирования API и backend-реализации

Файл скилла: `GEMINI.md` (в корневой директории)

---

## Полезные команды

### Docker

```bash
# Запуск всей системы
docker compose up --build

# Запуск только БД
docker compose up -d postgres

# Запуск в режиме разработки с live-reload для frontend
docker compose -f docker-compose.dev.yml up --build

# Запуск production-образа
docker compose -f docker-compose.prod.yml up --build
```

### Разработка

```bash
# Запуск pre-commit проверок
pre-commit run --all-files

# Миграции БД
python -m db.migrations_runner

# Создание новой миграции
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## Контакты и демо

- Email для демо: hello@stdo-demo.com
- Лендинг продукта: `stdo-landing.html` (можно открыть в браузере как статический файл)
