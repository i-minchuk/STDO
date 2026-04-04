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

### 1. Start the database

```bash
cd STDO
docker compose up -d
```

### 2. Install dependencies

#### Option 1: virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For development and linting, install dev dependencies as well:

```bash
pip install -r requirements-dev.txt
```

#### Option 2: conda

```bash
conda env create -f environment.yml
conda activate iris
./scripts/setup_dev.sh
```

On Windows PowerShell:

```powershell
conda env create -f environment.yml
conda activate iris
scripts\setup_dev.ps1
```

Then install frontend dependencies separately in `frontend`:

```bash
cd frontend
npm ci
```

### 3. Create a local `.env` file

Copy the example file and adjust values if necessary:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 4. Run migrations

```bash
python -m db.migrations_runner
```

### 5. Start the server

```bash
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

### 6. (Optional) Load sample data

```bash
python -m project.scripts.init_sample_project
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
docker compose -f docker-compose.prod.yml up --build
```

For local development with live frontend reload, use the dev compose file and run the frontend from the browser at http://localhost:5173:

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
