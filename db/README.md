# Database Layer

Database connection, migrations, and utilities for DokPotok IRIS.

## Overview

The `db` module provides PostgreSQL connectivity and migration management using:
- `psycopg` for async database operations
- `Alembic` for schema migrations
- Connection pooling for performance

## Architecture

```
┌─────────────────┐
│  Services       │  ← Business logic
└────────┬────────┘
         │ uses
┌────────▼────────┐
│ Repositories    │  ← Data access
└────────┬────────┘
         │ uses
┌────────▼────────┐
│    Database     │  ← Connection pool, SQL execution
└─────────────────┘
```

## Database Connection

**File**: `database.py`

**Features**:
- Async connection pooling
- Automatic timezone (UTC)
- Transaction management
- Query execution helpers

**Configuration**:
```python
from db.database import Database

db = Database(
    dsn="postgresql://user:pass@localhost:5432/iris",
    min_size=2,
    max_size=10
)
db.connect()
```

**Usage**:
```python
# Fetch one row
row = db.fetch_one("SELECT * FROM projects WHERE id = %s", (1,))

# Fetch multiple rows
rows = db.fetch_all("SELECT * FROM projects WHERE status = %s", ("active",))

# Execute (INSERT/UPDATE/DELETE)
result = db.execute("UPDATE projects SET status = %s WHERE id = %s", ("completed", 1))

# Transaction
with db.transaction():
    db.execute("INSERT INTO projects ...")
    db.execute("INSERT INTO tasks ...")
    # All or nothing
```

## Migrations

### Alembic Migrations

**Location**: `alembic/versions/`

**Current Migrations**:
1. `0001_initial_schema.py` - Initial schema (users, projects, documents, etc.)
2. `0002_add_tenders.py` - Tenders module
3. `0003_add_project_metrics.py` - Project metrics table

**Running Migrations**:
python -m db.migrations_runner

# Or via Alembic directly
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

**Creating New Migration**:
alembic revision --autogenerate -m "Add new table"

# Manual migration
alembic revision -m "Add column to projects"
```

**Migration Best Practices**:
1. **Test migrations**: Always test on fresh database
2. **Idempotent**: Use `IF EXISTS`, `IF NOT EXISTS`
3. **No destructive changes**: Avoid DROP TABLE/COLUMN
4. **Data migrations**: Use separate scripts for data changes
5. **Rollback**: Always test downgrade path

### SQL Migrations (Legacy)

**Location**: `db/migrations/`

**Status**: Legacy SQL scripts, kept for reference. Alembic is the source of truth.

**Files**:
- `000_initial.sql` - Initial schema
- `001_add_planning.sql` - Planning tables
- `002_add_performance_indexes.sql` - Performance indexes
- `002_add_users.sql` - Users table
- `003_new_modules.sql` - New modules (gamification, etc.)
- `004_additional_performance_indexes.sql` - Additional indexes

**Note**: For new changes, use Alembic migrations, not SQL scripts.

## Connection Pooling

**Default Configuration**:
- `min_size`: 2 connections
- `max_size`: 10 connections
- `timeout`: 30 seconds

**Tune for Production**:
```python
db = Database(
    dsn=...,
    min_size=5,   # More connections for production
    max_size=50   # Handle higher load
)
```

## Timezone Handling

All timestamps use UTC:

```sql
-- PostgreSQL configuration
SET timezone = 'UTC';
```

**Python**:
```python
from core.datetime_utils import utc_now

now = utc_now()  # Always UTC
```

## Query Optimization

### Indexes

Key indexes for performance:

```sql
-- Documents by project and status
CREATE INDEX idx_documents_project_status ON documents(project_id, status);

-- Tasks by assignee and status
CREATE INDEX idx_tasks_assignee_status ON planned_tasks(assigned_to, status);

-- Notifications unread count (partial index)
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) 
WHERE is_read = false;

-- Gamification events by user and date
CREATE INDEX idx_gamification_events_user_date ON gamification_events(user_id, created_at DESC);
```

### Query Patterns

**Avoid N+1**: Use JOINs and GROUP BY:

```python
# BAD: N+1 queries
for project in projects:
    tasks = repo.get_by_project_id(project.id)

# GOOD: Single query
tasks = db.fetch_all("""
    SELECT p.*, t.* 
    FROM projects p
    LEFT JOIN planned_tasks t ON t.project_id = p.id
    WHERE p.status = %s
""", ("active",))
```

**Use Transactions**:

```python
with db.transaction():
    # All operations succeed or all rollback
    repo1.insert(...)
    repo2.update(...)
```

## Testing

**Unit Tests**: Use mocks:

```python
def test_get_by_id(repo, mock_db):
    mock_db.fetch_one.return_value = {"id": 1, "name": "Test"}
    result = repo.get_by_id(1)
    assert result.name == "Test"
```

**Integration Tests**: Use real database:

```python
@pytest.mark.integration
def test_create_and_retrieve(test_locator, cleanup_test_db):
    project = test_locator.project_repo.insert(...)
    retrieved = test_locator.project_repo.get_by_id(project.id)
    assert retrieved.code == project.code
```

## Configuration

**Environment Variables**:
```bash
DB_DSN=postgresql://user:pass@localhost:5432/iris
DB_TEST_DSN=postgresql://user:pass@localhost:5432/iris_test
```

**Connection String Format**:
```
postgresql://user:password@host:port/database
```

## Troubleshooting

### Connection Errors

**Symptom**: `connection refused`

**Solution**:
1. Check PostgreSQL is running
2. Verify DB_DSN is correct
3. Check firewall/port 5432

### Migration Errors

**Symptom**: `migration already applied`

**Solution**:
```bash
# Reset migration state
alembic stamp head

# Or downgrade and reapply
alembic downgrade base
alembic upgrade head
```

### Slow Queries

**Diagnosis**:
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';

-- Check slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

**Solution**:
1. Add missing indexes
2. Optimize queries
3. Increase pool size
