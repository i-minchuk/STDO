"""Tests for CPM scheduler service using mock database."""

from datetime import date
from unittest.mock import MagicMock

from models.enums import TaskStatus, TaskType
from models.planned_task import PlannedTask
from models.task_dependency import TaskDependency
from services.cpm_scheduler_service import CPMSchedulerService


def _make_task(task_id: int, duration: int = 5) -> PlannedTask:
    return PlannedTask(
        id=task_id,
        project_id=1,
        project_code="PRJ-001",
        project_name="Test",
        document_id=None,
        document_code=None,
        revision_id=None,
        revision_index=None,
        name=f"Task-{task_id}",
        task_type=TaskType.ENGINEERING,
        assigned_to=1,
        owner_name="Test",
        duration_days_planned=duration,
        work_hours_planned=float(duration * 8),
        start_date_planned=date(2026, 1, 1),
        end_date_planned=date(2026, 1, 1),
        start_date_actual=None,
        end_date_actual=None,
        percent_complete=0,
        status=TaskStatus.NOT_STARTED,
    )


def _make_dep(pred_id: int, succ_id: int, lag: int = 0) -> TaskDependency:
    return TaskDependency(
        id=0,
        project_id=1,
        predecessor_task_id=pred_id,
        successor_task_id=succ_id,
        dependency_type="FS",
        lag_days=lag,
    )


def test_single_task_cpm():
    """Single task with no dependencies: slack = 0, it is critical."""
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    task_repo = MagicMock()
    dep_repo = MagicMock()

    task_repo.get_by_project_id.return_value = [_make_task(1, duration=3)]
    dep_repo.get_for_project.return_value = []

    scheduler = CPMSchedulerService(db, task_repo, dep_repo)
    critical = scheduler.recalculate_project_schedule(project_id=1)

    assert critical == [1]
    task_repo.update_cpm_fields.assert_called_once()
    updated_tasks = task_repo.update_cpm_fields.call_args[0][0]
    assert updated_tasks[0].es == 0
    assert updated_tasks[0].ef == 3
    assert updated_tasks[0].ls == 0
    assert updated_tasks[0].lf == 3
    assert updated_tasks[0].slack == 0


def test_linear_chain_cpm():
    """A -> B -> C: all tasks are critical."""
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    task_repo = MagicMock()
    dep_repo = MagicMock()

    tasks = [_make_task(1, 3), _make_task(2, 5), _make_task(3, 2)]
    deps = [_make_dep(1, 2), _make_dep(2, 3)]

    task_repo.get_by_project_id.return_value = tasks
    dep_repo.get_for_project.return_value = deps

    scheduler = CPMSchedulerService(db, task_repo, dep_repo)
    critical = scheduler.recalculate_project_schedule(project_id=1)

    assert set(critical) == {1, 2, 3}

    updated = task_repo.update_cpm_fields.call_args[0][0]
    t1 = next(t for t in updated if t.id == 1)
    t2 = next(t for t in updated if t.id == 2)
    t3 = next(t for t in updated if t.id == 3)

    assert t1.es == 0 and t1.ef == 3
    assert t2.es == 3 and t2.ef == 8
    assert t3.es == 8 and t3.ef == 10


def test_parallel_paths_cpm():
    """
    A(3) -> C(2)
    B(5) -> C(2)
    B path is longer, so A has slack, B is critical.
    """
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    task_repo = MagicMock()
    dep_repo = MagicMock()

    tasks = [_make_task(1, 3), _make_task(2, 5), _make_task(3, 2)]
    deps = [_make_dep(1, 3), _make_dep(2, 3)]

    task_repo.get_by_project_id.return_value = tasks
    dep_repo.get_for_project.return_value = deps

    scheduler = CPMSchedulerService(db, task_repo, dep_repo)
    critical = scheduler.recalculate_project_schedule(project_id=1)

    # B(5) -> C(2) = 7 days total; A(3) -> C(2) = 5 days
    # So B and C are critical, A has slack = 2
    assert 2 in critical  # B
    assert 3 in critical  # C
    assert 1 not in critical  # A has slack

    updated = task_repo.update_cpm_fields.call_args[0][0]
    t1 = next(t for t in updated if t.id == 1)
    assert t1.slack == 2


def test_empty_project_cpm():
    """No tasks => empty result."""
    db = MagicMock()
    task_repo = MagicMock()
    dep_repo = MagicMock()

    task_repo.get_by_project_id.return_value = []
    dep_repo.get_for_project.return_value = []

    scheduler = CPMSchedulerService(db, task_repo, dep_repo)
    critical = scheduler.recalculate_project_schedule(project_id=1)

    assert critical == []


def test_cpm_with_lag():
    """A -> B with 2-day lag: B starts at day 5 (3 + 2)."""
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    task_repo = MagicMock()
    dep_repo = MagicMock()

    tasks = [_make_task(1, 3), _make_task(2, 4)]
    deps = [_make_dep(1, 2, lag=2)]

    task_repo.get_by_project_id.return_value = tasks
    dep_repo.get_for_project.return_value = deps

    scheduler = CPMSchedulerService(db, task_repo, dep_repo)
    critical = scheduler.recalculate_project_schedule(project_id=1)

    updated = task_repo.update_cpm_fields.call_args[0][0]
    t2 = next(t for t in updated if t.id == 2)
    assert t2.es == 5  # 3 + 2 lag
    assert t2.ef == 9  # 5 + 4
