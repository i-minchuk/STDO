# STDO — Technical Documentation Management System

System for managing technical documentation (drawings, PDFs, specifications) with project planning, CPM scheduling, and revision workflow control.

## Features

- **Document management** — create documents, track revisions (A01, A02, B01...), approval workflows
- **Project planning** — CPM (Critical Path Method) scheduling with forward/backward pass
- **Task management** — engineering, review, approval tasks with dependencies
- **Portfolio dashboard** — overview of all projects, SPI/CPI metrics, risk levels
- **Gamification** — engineer metrics, points, XP tracking

## Stack

- Python 3.12+
- FastAPI
- PostgreSQL 15 (via psycopg 3)
- Pydantic v2

## Quick Start

### 1. Start the database

```bash
cd project
docker-compose up -d
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python -m db.migrations_runner
```

### 4. Start the server

```bash
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

### 5. (Optional) Load sample data

```bash
python -m project.scripts.init_sample_project
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_DSN` | `postgresql://dms_user:dms_pass@localhost:5432/dms` | PostgreSQL connection string |
| `STORAGE_ROOT` | `./data/docs` | Directory for storing revision files |
| `LOG_LEVEL` | `INFO` | Logging level |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects/` | List all projects |
| GET | `/api/projects/portfolio/today` | Portfolio overview |
| POST | `/api/documents/{id}/revisions` | Create revision with file upload |
| POST | `/api/revisions/{id}/approve` | Approve a revision |
| POST | `/api/internal/projects/{id}/recalc_cpm_and_metrics` | Recalculate CPM schedule |
| GET | `/health` | Health check |

## Architecture

```
api/           FastAPI route handlers
core/          Service locator (DI container)
db/            Database connection and migrations
dto/           Pydantic DTOs (API request/response schemas)
models/        Domain models (dataclasses)
repositories/  Data access layer (SQL queries via psycopg)
services/      Business logic layer
```

## Running Tests

```bash
pytest tests/ -v
```
