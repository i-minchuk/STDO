# Services Layer

Business logic layer for DokPotok IRIS.

## Overview

Services contain the core business logic of the application. They:
- Orchestrate repositories and other services
- Implement use cases and workflows
- Handle transactions and error handling
- Enforce business rules and validation

## Architecture

```
┌─────────────────┐
│     API         │  ← HTTP endpoints
└────────┬────────┘
         │ calls
┌────────▼────────┐
│   Services      │  ← Business logic
└────────┬────────┘
         │ uses
┌────────▼────────┐
│  Repositories   │  ← Data access
└─────────────────┘
```

## Services

### Document Workflow

**File**: `document_workflow_service.py`

**Purpose**: Manage document lifecycle from creation to approval.

**Key Methods**:
- `create_revision_with_workflow()` - Create revision with CPM tasks
- `approve_revision_with_workflow_dto()` - Approve revision and complete tasks

**Transaction Safety**:
```python
with self._db.transaction():
    revision = self._revision_service.create_revision(...)
    tasks = self._cpm.create_tasks_for_revision(...)
    # All or nothing
```

### Revision Management

**File**: `revision_service.py`

**Purpose**: Handle document versioning and file storage.

**Key Methods**:
- `create_revision()` - Create new revision with file upload
- `approve_revision()` - Approve revision and mark previous as superseded

**Versioning**:
- Major revisions: New letter (A→B)
- Minor revisions: Increment number (A01→A02)

### Project Dashboard

**File**: `project_dashboard_service.py`

**Purpose**: Calculate project metrics and portfolio overview.

**Key Methods**:
- `get_portfolio_today_overview_dto()` - Portfolio status with caching
- `recalculate_project_metrics()` - SPI, CPI, risk levels

**Performance**:
- Uses single optimized query (no N+1)
- Caching with 5-minute TTL
- Cache invalidation on task updates

### CPM Scheduler

**File**: `cpm_scheduler_service.py`

**Purpose**: Calculate Critical Path Method for project scheduling.

**Key Methods**:
- `calculate_cpm()` - ES, EF, LS, LF, slack for all tasks
- `get_critical_tasks()` - Tasks with slack = 0
- `recalculate_project()` - Full project recalculation

**Algorithm**:
1. Forward pass: Calculate ES, EF
2. Backward pass: Calculate LS, LF
3. Slack = LS - ES
4. Critical path: slack = 0

### Time Calculation

**File**: `time_calculation_service.py`

**Purpose**: Work day and hour calculations.

**Key Methods**:
- `calculate_work_days_from_hours()` - Hours → days
- `calculate_end_date()` - Start + duration
- `is_work_day()` - Check if date is work day

**Schedule Integration**:
- Respects work schedule (weekends, holidays)
- Uses default or custom schedule

### Gamification

**File**: `gamification_event_service.py` (if implemented)

**Purpose**: Track user achievements and rewards.

**Key Features**:
- Event tracking with deduplication
- Score calculation
- Badge unlocking
- Daily quests

### Heatmap

**File**: `heatmap_service.py`

**Purpose**: Visualize user workload over time.

**Key Methods**:
- `generate_weekly_heatmap()` - Week-by-week view
- `generate_monthly_heatmap()` - Month view
- `get_user_activity_summary()` - Activity stats

## Service Locator

Services are managed via `ServiceLocator` (in `core/service_locator.py`):

```python
from core.service_locator import get_locator

locator = get_locator()
workflow = locator.document_workflow
revision = locator.revision_service
dashboard = locator.project_dashboard
```

## Transaction Management

Transactions are explicit in services:

```python
def create_revision_with_workflow(self, ...):
    with self._db.transaction():
        # All operations in transaction
        revision = self._revision_service.create_revision(...)
        tasks = self._cpm.create_tasks_for_revision(...)
        # On exception: rollback
```

## Caching

Some services use caching for performance:

```python
from core.cache import cached, invalidate_cache

class ProjectDashboardService:
    @cached(ttl=300, key_prefix="portfolio")
    def get_portfolio_today_overview_dto(self, target_date):
        # Cached for 5 minutes
        ...
    
    def invalidate_portfolio_cache(self, project_id=None):
        invalidate_cache("cache:project_dashboard_service:*")
```

## Testing

Services are tested with mocked repositories:

```python
def test_recalculate_metrics_with_tasks(self, service, mock_task_repo):
    mock_task_repo.get_by_project_id.return_value = tasks
    result = service.recalculate_project_metrics(1)
    assert result["spi"] == 0.85
```

## Best Practices

1. **Keep services thin**: Business logic in domain models when possible
2. **Use transactions**: Wrap multi-step operations
3. **Cache strategically**: Cache expensive queries
4. **Validate early**: Check preconditions at method start
5. **Log appropriately**: INFO for workflows, WARNING for recoverable errors
