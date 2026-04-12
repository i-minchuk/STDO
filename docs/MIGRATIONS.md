# Database Migrations Guide

## Overview

DokPotok IRIS uses **Alembic** for database migrations. This document explains how to work with migrations.

## ⚠️ Current State: Two Migration Systems (Known Issue)

This project has **TWO** migration systems:

1. **Alembic** (`alembic/versions/`) — 3 migrations — **OFFICIAL**
2. **SQL Scripts** (`db/migrations/`) — 6 scripts — **LEGACY**

### Status Summary

| System | Files | Status | Action Required |
|--------|-------|--------|-----------------|
| Alembic | 0001, 0002, 0003 | Active, source of truth | ✅ Use for new changes |
| SQL Scripts | 000-004 | Legacy, reference only | 📋 Migrate to Alembic (optional) |

### What Each System Contains

**Alembic 0001** consolidates:
- `000_initial.sql` ✅
- `001_add_planning.sql` ✅
- `002_add_users.sql` ✅
- `003_new_modules.sql` ✅

**Alembic 0002, 0003**: Additional tables (tenders, metrics)

**SQL Scripts NOT in Alembic** (indexes only):
- `002_add_performance_indexes.sql` — Indexes for N+1 prevention
- `004_additional_performance_indexes.sql` — Additional gamification/notification indexes

### Gap Analysis

| SQL Migration | Content | In Alembic? | Action |
|---------------|---------|-------------|--------|
| 000_initial.sql | Tables | ✅ Yes (0001) | Keep for reference |
| 001_add_planning.sql | Planning tables | ✅ Yes (0001) | Keep for reference |
| 002_add_users.sql | Users | ✅ Yes (0001) | Keep for reference |
| 003_new_modules.sql | Gamification, etc. | ✅ Yes (0001) | Keep for reference |
| **002_add_performance_indexes.sql** | **Indexes** | ✅ **MIGRATED (0004)** | **Mark as MIGRATED** |
| **004_additional_performance_indexes.sql** | **Indexes** | ✅ **MIGRATED (0004)** | **Mark as MIGRATED** |

**MIGRATION COMPLETE**: Indexes from 002 and 004 have been migrated to Alembic revision `87350b5f2a4a_add_performance_indexes.py`.

---

## Migration Plan: SQL Indexes → Alembic

### Phase 1: Migrate Indexes (Recommended)

**Goal**: Move all SQL index migrations to Alembic.

**Steps**:

1. **Create Alembic migration for indexes**:
   ```bash
   alembic revision -m "add_performance_indexes"
   ```

2. **Copy indexes from SQL to Python**:
   ```python
   def upgrade():
       # From 002_add_performance_indexes.sql
       op.execute("CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id)")
       op.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON planned_tasks(project_id)")
       # ... all indexes from 002 ...
       
       # From 004_additional_performance_indexes.sql  
       op.execute("CREATE INDEX IF NOT EXISTS idx_gamification_events_user_points ON gamification_events (user_id) INCLUDE (points_delta)")
       # ... all indexes from 004 ...
   
   def downgrade():
       op.execute("DROP INDEX IF EXISTS idx_documents_project_id")
       # ... reverse all indexes ...
   ```

3. **Test migration**:
   ```bash
   # Fresh DB
   createdb iris_test
   alembic upgrade head --database postgresql://localhost/iris_test
   
   # Verify indexes
   psql -d iris_test -c "SELECT indexname FROM pg_indexes WHERE tablename = 'documents'"
   ```

4. **Deprecate SQL scripts**:
   - Add warning at top of SQL files
   - Update README to point to Alembic

### Phase 2: Long-term Cleanup (Optional)

**Goal**: Remove SQL migration files entirely.

**Steps**:
1. Confirm all indexes in Alembic
2. Move SQL files to `docs/archive/migrations/`
3. Update any references in CI/CD

---

## Running Migrations

### Apply All Migrations

Migrations run automatically on application startup:

```python
# In main.py
from db.migrations_runner import run_migrations
run_migrations()
```

Or manually:

```bash
python -m db.migrations_runner
```

### Manual Alembic Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Apply one migration at a time
alembic upgrade +1

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 0002_add_tenders

# Show current revision
alembic current

# Show migration history
alembic history

# Show details of pending migrations
alembic upgrade head --sql
```

---

## Migration Checklist (Before Committing)

### ✅ Required

- [ ] Migration tested on fresh database
- [ ] Downgrade path tested
- [ ] No data loss risks
- [ ] Indexes added for new columns
- [ ] Foreign keys have constraints
- [ ] Default values provided for NOT NULL columns
- [ ] Migration file named correctly (e.g., `0004_add_indexes.py`)
- [ ] Migration message is descriptive
- [ ] No sensitive data in migration
- [ ] Backup strategy documented

### ⚠️ For Index Migrations Only

- [ ] Index names follow convention `idx_<table>_<column>`
- [ ] Partial indexes documented (WHERE clauses)
- [ ] Included columns specified (INCLUDE)
- [ ] No duplicate indexes (check with `pg_indexes`)
- [ ] Index usage monitored after deploy (`pg_stat_user_indexes`)

### ❌ What NOT to Do

- ❌ Don't use SQL scripts for schema changes
- ❌ Don't commit migrations without testing
- ❌ Don't use autogenerate without reviewing
- ❌ Don't drop columns/tables without backup
- ❌ Don't change data without migration script
- ❌ Don't mix Alembic and SQL for same change

---

## Creating New Migrations

### Step 1: Make Model Changes

Edit models in `models/` directory.

### Step 2: Generate Migration

**Manual Migration (Recommended)**:

Since `target_metadata = None` in `env.py`, autogenerate is disabled. Create migration manually:

```bash
alembic revision -m "Add priority to projects"
```

Edit the generated file in `alembic/versions/`:

```python
def upgrade():
    op.add_column('projects', sa.Column('priority', sa.Integer(), nullable=True))
    
def downgrade():
    op.drop_column('projects', 'priority')
```

**For Index Migrations**:

```bash
alembic revision -m "add_performance_indexes"
```

Copy index SQL from `db/migrations/*.sql` to Python:

```python
def upgrade():
    # From 002_add_performance_indexes.sql
    op.execute("CREATE INDEX IF NOT EXISTS idx_documents_project_id ON documents(project_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON planned_tasks(project_id)")

def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_documents_project_id")
    op.execute("DROP INDEX IF EXISTS idx_tasks_project_id")
```

---

## Avoiding Confusion While Both Systems Exist

Until SQL migrations are fully migrated:

### ✅ DO

- Use **Alembic for ALL new changes**
- Reference Alembic in documentation
- If you add indexes, add them to Alembic, not SQL
- Check `alembic history` before creating migration

### ❌ DON'T

- Don't create new SQL migration files
- Don't run SQL migrations manually on production
- Don't mix Alembic and SQL for same change
- Don't assume SQL = Alembic (they diverged)

### 📋 If You Find SQL Migration Not in Alembic

1. Check if it's just indexes (OK to migrate later)
2. Check if it's schema change (BLOCKING - migrate immediately)
3. Create Alembic migration
4. Add comment to SQL file: "MIGRATED to Alembic 000X"
