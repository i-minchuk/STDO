# ДокПоток IRIS — Система управления инженерной документацией 

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

### Windows (Recommended)

#### Option 1: One-click launcher

1. **Double-click `start_iris.bat`** in the project root

This will:
- Check Python virtual environment
- Run database migrations
- Start backend server (http://localhost:8000)
- Start frontend server (http://localhost:5173)
- Open browser with API docs

#### Option 2: Setup script + launcher

```batch
REM Install all dependencies (Python + Node)
scripts\setup_dev.bat

REM Then start the app
start_iris.bat
```

#### Launcher modes:

```batch
start_iris.bat           # Full dev mode (backend + frontend)
start_iris.bat backend   # Backend only
start_iris.bat frontend  # Frontend only
start_iris.bat migrate   # Run migrations only
```

### Linux/macOS

#### Option 1: Manual setup

```bash
cd STDO

# 1. Start database (Docker)
docker compose up -d postgres

# 2. Create virtualenv
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # optional

# 4. Setup frontend
cd frontend
npm ci
cd ..

# 5. Create .env file
cp .env.example .env

# 6. Run migrations
python -m db.migrations_runner

# 7. Start backend
uvicorn main:app --reload

# 8. (Optional) Start frontend separately
cd frontend && npm run dev
```

## Configuration

Configuration values can be set via environment variables or a `.env` file in the project root.

| Variable | Default | Description |
|----------|---------|-------------|
| `IRIS_DB_DSN` | `postgresql://postgres:Qwerty852@localhost:5432/iris` | PostgreSQL connection string |
| `IRIS_STORAGE_ROOT` | `./storage` | Directory for storing revision files |
| `IRIS_SECRET_KEY` | `iris-secret-key-change-in-production` | JWT secret key for auth services |
| `IRIS_LOG_LEVEL` | `INFO` | Logging level |
| `TEST_DB_DSN` | `postgresql://postgres:Qwerty852@localhost:5432/iris_test` | PostgreSQL DSN for integration tests |

Example `.env` values are available in `.env.example`.

For frontend local development, copy `frontend/.env.example` to `frontend/.env`.

### Run with Docker Compose

Start the local database and backend. The Docker image builds the frontend assets and serves them from the backend container:

```bash
docker compose up --build
```

For a production-like stack, use the production compose file:

```bash
docker compose -f docker-compose.production.yml up --build
```

For local development with live frontend reload, use dev container (recommended) or run frontend separately:

```bash
# Option 1: Use dev container (recommended)
# Open in VS Code and choose "Reopen in Container"

# Option 2: Run frontend separately
cd frontend
npm run dev
# Then start backend:
python main.py
```

To run pre-commit checks:

```bash
python -m pre_commit install
python -m pre_commit run --all-files
```

For local development with live frontend reload, use the dev compose file and run the frontend from the browser at http://localhost:5432
:

```bash
docker compose -f docker-compose.dev.yml up --build
```

To run pre-commit checks in the development compose environment:

```bash
docker compose -f docker-compose.dev.yml run --rm precommit
```

### VS Code Dev Container

Open the repository in VS Code and choose `Reopen in Container`.
This will build a development container with Python 3.12, Node.js 20, install backend and frontend dependencies automatically, and run `pre-commit` against all files once.

VS Code task definitions are included in `.vscode/tasks.json`.
Use the Command Palette to run tasks such as:
- `Start backend`
- `Start frontend`
- `Start full dev stack`

The dev container also starts backend and frontend dev servers automatically after it finishes provisioning.

If you want to start manually:

```bash
code .
```

Then select the Dev Container option from the VS Code command palette.

Then open the API docs at:

```bash
http://localhost:8000/docs
```

### Run integration tests

The integration suite requires a real PostgreSQL database. Set `TEST_DB_DSN` in `.env` and then run:

```bash
pytest -m integration -q
```

On Windows PowerShell:

```powershell
$env:TEST_DB_DSN = "postgresql://postgres:Qwerty852@localhost:5432/iris_test"
pytest -m integration -q
```

## CI

A GitHub Actions workflow is configured in `.github/workflows/ci.yml`.
It runs linting, unit tests, builds the Docker image, and executes integration tests against a PostgreSQL service.

## Linting

Backend Python linting and formatting checks are available via `ruff`, `black` and `pre-commit`:

```bash
pip install -r requirements-dev.txt
python -m ruff check .
python -m black --check .
python -m pre_commit install
python -m pre_commit run --all-files
```

The `pre-commit` hooks also include frontend checks for:
- `npm run lint`
- `npm run build`

Frontend linting and build verification are additionally available in the `frontend` folder:

```bash
cd frontend
npm ci
npm run lint
npm run build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects/` | List all projects |
| GET | `/api/projects/portfolio/today` | Portfolio overview |
| POST | `/api/documents/{id}/revisions` | Create revision with file upload |
| POST | `/api/revisions/{id}/approve` | Approve a revision |
| POST | `/api/internal/projects/{id}/recalc_cpm_and_metrics` | Recalculate CPM schedule |
| GET | `/api/health` | Health check |
| GET | `/docs` | Swagger API documentation |

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
