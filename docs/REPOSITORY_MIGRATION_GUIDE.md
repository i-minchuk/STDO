# Repository Migration to BaseRepository Guide

## Overview

This guide explains how to migrate existing repositories to use `BaseRepository` for reduced boilerplate and consistent patterns.

## Current State

**Migrated to BaseRepository**:
- ✅ `work_schedule_repository.py` - Simple CRUD + date calculations
- ✅ `notification_repository.py` - Simple CRUD + unread count
- ✅ `vdr_mdr_repository.py` - UPSERT with ON CONFLICT + pagination

**Remaining repositories** (14 total):
- `project_repository.py` - Medium complexity
- `document_repository.py` - Medium complexity
- `revision_repository.py` - Medium complexity
- `tender_repository.py` - Medium complexity
- `gamification_*_repository.py` - Various complexity
- `task_*_repository.py` - Various complexity
- `time_log_repository.py` - Medium complexity
- `remark_repository.py` - Medium complexity
- `user_repository.py` - Simple CRUD
- `combo_achievement_repository.py` - Simple CRUD
- `daily_quest_repository.py` - Simple CRUD
- `gamification_event_repository.py` - Simple CRUD
- `gamification_badge_repository.py` - Simple CRUD
- `planned_task_repository.py` - High complexity (CPM)

## Why Migrate to BaseRepository?

### Benefits

| Benefit | Impact |
|---------|--------|
| **Reduced boilerplate** | 50-70% less code |
| **Consistent patterns** | Easier onboarding |
| **Less code to test** | Faster test development |
| **Built-in pagination** | No duplicate code |
| **Type safety** | Generic type hints |

### Trade-offs

| Trade-off | Impact |
|-----------|--------|
| **Less flexibility** | Custom queries still possible |
| **Learning curve** | 1-2 hours per developer |
| **Migration effort** | 2-4 hours per repository |
| **BaseRepository complexity** | Need to understand generics |

## Migration Priority (Updated)

**Already migrated** (3 repos):
| Repository | Complexity | Notes |
|------------|------------|-------|
| work_schedule_repository.py | Low | Date calculations kept |
| notification_repository.py | Low | Unread count logic kept |
| vdr_mdr_repository.py | Medium | UPSERT with ON CONFLICT |

**Recommended for next migration**:
| Priority | Repository | Complexity | Est. Hours | Reason |
|----------|------------|------------|------------|--------|
| **1** | `user_repository.py` | Low | 2-3 | Simple CRUD |
| **2** | `daily_quest_repository.py` | Low | 2-3 | Simple CRUD |
| **3** | `gamification_badge_repository.py` | Low | 2-3 | Simple CRUD |
| **4** | `combo_achievement_repository.py` | Low | 2-3 | Simple CRUD |
| **5** | `project_repository.py` | Medium | 3-4 | Has pagination |

## Migration Checklist

Before starting:

- [ ] Repository has unit tests
- [ ] Repository has integration tests (optional but recommended)
- [ ] BaseRepository is stable and tested
- [ ] You understand the repository's custom methods

During migration:

- [ ] Extend BaseRepository with custom columns
- [ ] Keep custom business logic methods
- [ ] Remove duplicate CRUD code
- [ ] Run existing tests
- [ ] Add tests for BaseRepository methods
- [ ] Update documentation

After migration:

- [ ] Code review
- [ ] Performance testing (if applicable)
- [ ] Update other developers
- [ ] Document any gotchas

## Step-by-Step Migration Example

### Example 1: Migrate `work_schedule_repository.py`

[Previous content...]

### Example 2: Migrate `notification_repository.py`

**Before** (100 lines):
```python
class NotificationRepository:
    def __init__(self, db):
        self._db = db
    _COLUMNS = "id, user_id, type, title, message, is_read, created_at, metadata"
    
    def insert(self, user_id, type, title, message, metadata=None):
        row = self._db.fetch_one(
            f"INSERT INTO notifications (...) VALUES (...) RETURNING {self._COLUMNS}",
            (...)
        )
        return self._row_to_model(row)
    
    def get_user_notifications(self, user_id, limit=20):
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )
        return [self._row_to_model(r) for r in rows]
    
    def get_unread_count(self, user_id):
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS count FROM notifications WHERE user_id = %s AND is_read = false",
            (user_id,)
        )
        return int(row["count"]) if row else 0
    
    @staticmethod
    def _row_to_model(row):
        return Notification(...)
```

**After** (~50 lines):
```python
class NotificationRepository(BaseRepository[Notification]):
    """Repository for notifications with BaseRepository for CRUD operations."""
    
    def __init__(self, db: Database) -> None:
        super().__init__(
            db=db,
            model_class=Notification,
            table_name="notifications",
            columns="id, user_id, type, title, message, is_read, created_at, metadata"
        )
    
    def insert(self, user_id, type, title, message, metadata=None):
        row = self._db.fetch_one(
            f"INSERT INTO {self._table_name} (...) VALUES (...) RETURNING {self._columns}",
            (...)
        )
        return self._row_to_model(row)
    
    def get_user_notifications(self, user_id, limit=20):
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )
        return [self._row_to_model(r) for r in rows]
    
    def get_unread_count(self, user_id):
        row = self._db.fetch_one(
            f"SELECT COUNT(*) AS count FROM {self._table_name} WHERE user_id = %s AND is_read = false",
            (user_id,)
        )
        return int(row["count"]) if row else 0
    
    # _row_to_model inherited from BaseRepository
```

**Changes**:
- Removed `_COLUMNS` constant
- Removed `_row_to_model` static method
- Updated SQL to use `self._table_name` and `self._columns`
- Saved ~50% code

### Example 3: Migrate `vdr_mdr_repository.py` (with UPSERT)

**Challenge**: UPSERT with `ON CONFLICT` requires special handling.

**Solution**: Keep custom `upsert` method, use BaseRepository for everything else.

```python
class VDRRepository(BaseRepository[VDREntry]):
    def __init__(self, db: Database) -> None:
        super().__init__(
            db=db,
            model_class=VDREntry,
            table_name="vdr_entries",
            columns="..."
        )
    
    def upsert(self, project_id, doc_number, ...):
        # Keep custom UPSERT logic
        row = self._db.fetch_one(
            f"INSERT INTO {self._table_name} (...) ON CONFLICT (...) DO UPDATE SET ... RETURNING {self._columns}",
            (...)
        )
        return self._row_to_model(row)
    
    def get_by_project_paginated(self, project_id, limit, offset):
        # Use BaseRepository._get_paginated
        return self._get_paginated(
            where_sql=" WHERE project_id=%s",
            params=(project_id,),
            order_by="doc_number",
            limit=limit,
            offset=offset
        )
```

**Key Insight**: Even with complex UPSERT, you still save boilerplate for other methods.

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Forgetting to pass `db` to super().__init__() | Always call `super().__init__(db=db, ...)` |
| Hardcoding table name in SQL | Use `self._table_name` |
| Hardcoding columns in SQL | Use `self._columns` |
| Overriding `_row_to_model` unnecessarily | Only override if JSON/Enum handling needed |
| Losing custom business logic | Keep all custom methods, only replace CRUD |
| Not running tests after migration | Always run existing tests after migration |

---

## Migration Timeline (Updated)

| Phase | Repositories | Duration | Milestone |
|-------|--------------|----------|-----------|
| **1** | work_schedule, notification, vdr_mdr | ✅ **COMPLETE** | 3 repos migrated |
| **2** | user, daily_quest, gamification_* | 1 week | Simple CRUD repos |
| **3** | project, document, revision, tender | 2 weeks | Medium complexity |
| **4** | task_*, time_log, remark, planned_task | 2 weeks | High complexity |

**Total**: ~5 weeks for full migration (optional, incremental)

## Success Criteria

- [ ] All migrated repositories pass existing tests
- [ ] Code coverage maintained or improved
- [ ] No performance regressions
- [ ] Developers comfortable with patterns
- [ ] Documentation up to date

## Support

For migration issues:
1. Check BaseRepository implementation
2. Review existing tests
3. Consult with team
4. Create issue if BaseRepository needs improvement

## Appendix: Full Repository List

See `repositories/README.md` for complete list with current status.
