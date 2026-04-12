# Repositories Layer

Data access layer for DokPotok IRIS.

## Overview

Repositories provide a clean interface between the business logic and the database. They handle:
- SQL query construction and execution
- Model serialization/deserialization
- Transaction management (via Database layer)

## Architecture

```
┌─────────────────┐
│   Services      │  ← Business logic
└────────┬────────┘
         │ uses
┌────────▼────────┐
│ Repositories    │  ← Data access
└────────┬────────┘
         │ uses
┌────────▼────────┐
│    Database     │  ← Connection pool, raw SQL
└─────────────────┘
```

## BaseRepository

`BaseRepository` provides common CRUD operations to reduce boilerplate.

### Usage

```python
from repositories.base_repository import BaseRepository
from models.project import Project

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db):
        super().__init__(
            db=db,
            model_class=Project,
            table_name="projects",
            columns="id, code, name, status, manager_id, start_date, end_date_planned"
        )
    
    # Now you have these methods for free:
    # - get_by_id(entity_id) -> Optional[Project]
    # - list_all(order_by="id") -> Sequence[Project]
    # - delete(entity_id) -> bool
```

### Custom Queries

For complex queries, add custom methods:

```python
class ProjectRepository(BaseRepository[Project]):
    def list_by_status(self, status: str) -> Sequence[Project]:
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} WHERE status = %s",
            (status,)
        )
        return [self._row_to_model(r) for r in rows]
```

## Current Repositories

| Repository | Model | BaseRepository | Custom Methods |
|------------|-------|----------------|----------------|
| `project_repository.py` | Project | ❌ | ✅ CRUD, pagination, filters |
| `document_repository.py` | Document | ❌ | ✅ CRUD, by project |
| `revision_repository.py` | DocumentRevision | ❌ | ✅ CRUD, versioning logic |
| `planned_task_repository.py` | PlannedTask | ❌ | ✅ CRUD, by project, CPM |
| `user_repository.py` | User | ❌ | ✅ CRUD, pagination |
| `work_schedule_repository.py` | WorkSchedule | ❌ | ✅ CRUD, date calculations |
| `tender_repository.py` | Tender | ❌ | ✅ CRUD, filters, documents |
| `remark_repository.py` | Remark | ❌ | ✅ CRUD, responses, pagination |
| `notification_repository.py` | Notification | ❌ | ✅ CRUD, unread count |
| `gamification_event_repository.py` | GamificationEvent | ❌ | ✅ CRUD, score, events |
| `gamification_badge_repository.py` | GamificationBadge | ❌ | ✅ CRUD, badges |
| `daily_quest_repository.py` | DailyQuest | ❌ | ✅ CRUD, quests |
| `combo_achievement_repository.py` | ComboAchievement | ❌ | ✅ CRUD, combos |
| `time_log_repository.py` | TimeLog | ❌ | ✅ CRUD, time tracking |
| `task_dependency_repository.py` | TaskDependency | ❌ | ✅ CRUD, dependencies |
| `vdr_mdr_repository.py` | VDR/MDR | ❌ | ✅ CRUD, verification |

## Patterns

### Row to Model Conversion

All repositories use `_row_to_model()` to convert database rows to model instances:

```python
@staticmethod
def _row_to_model(row: dict) -> YourModel:
    if not row:
        return None
    return YourModel.from_row(row)  # or YourModel(**row)
```

### Pagination

Use `_get_paginated()` for list endpoints:

```python
def list_projects(self, limit: int = 20, offset: int = 0) -> tuple[Sequence[Project], int]:
    return self._get_paginated(
        where_sql=" WHERE status = %s",
        params=(status,),
        order_by="created_at DESC",
        limit=limit,
        offset=offset
    )
```

### Transactions

Transactions are managed at the service level, not in repositories:

```python
# In service (correct)
with self._db.transaction():
    repo1.insert(...)
    repo2.update(...)

# Not in repository
```

## Testing

Repositories are tested with mocks:

```python
def test_get_by_id(self, repo, mock_db):
    mock_db.fetch_one.return_value = {"id": 1, "name": "Test"}
    result = repo.get_by_id(1)
    assert result.name == "Test"
```

Integration tests use real database:

```python
def test_create_and_retrieve(test_locator, cleanup_test_db):
    project = test_locator.project_repo.insert(...)
    retrieved = test_locator.project_repo.get_by_id(project.id)
    assert retrieved.code == project.code
```

## Migration to BaseRepository

If you want to migrate a repository to use BaseRepository:

1. Identify reusable CRUD patterns
2. Extend BaseRepository with custom columns
3. Keep custom business logic methods
4. Run tests to verify compatibility
5. Update documentation

**Note**: Migration is optional. Current implementation is stable and well-tested.
