"""Tests for API endpoints using FastAPI TestClient."""

from unittest.mock import MagicMock, patch
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from models.project import Project
from models.user import User
from models.enums import ProjectStatus


@pytest.fixture
def client():
    """Create a test client with mocked service locator."""
    mock_locator = MagicMock()

    # Mock project_repo.list_all_paginated
    mock_locator.project_repo.list_all_paginated.return_value = (
        [
            Project(
                id=1, code="PRJ-001", name="Test Project",
                customer="Test", status=ProjectStatus.ACTIVE,
                manager_id=1, start_date=date(2026, 1, 1),
                end_date_planned=date(2026, 12, 31),
                end_date_forecast=None, end_date_actual=None,
                created_at=datetime(2026, 1, 1),
            )
        ],
        1,
    )

    # Mock project_repo.insert
    mock_project = Project(
        id=2, code="PRJ-2026-001", name="Test Tender",
        customer="Test Customer", status=ProjectStatus.PLANNED,
        manager_id=1, start_date=date.today(),
        end_date_planned=date(2026, 12, 31),
        end_date_forecast=None, end_date_actual=None,
        created_at=datetime.now(),
        custom_fields={"customer_specific": "value"},
        vdr_required=True, otk_required=True,
        crs_deadline_days=3, logistics_delivery_weeks=2,
        logistics_complexity="normal",
    )
    mock_locator.project_repo.insert.return_value = mock_project
    mock_locator.project_repo.list_all.return_value = []

    mock_locator.planned_task_repo.get_all.return_value = []
    mock_locator.planned_task_repo.insert.return_value = MagicMock()

    mock_locator.cpm_scheduler.recalculate_project_schedule.return_value = []
    mock_locator.project_dashboard.recalculate_project_metrics.return_value = None
    mock_locator.gamification_event_repo.insert.return_value = MagicMock()
    mock_locator.gamification_badge_repo.get_user_badges.return_value = []
    mock_locator.gamification_badge_repo.award_badge_if_not_exists.return_value = None
    mock_locator.notification_repo.insert.return_value = MagicMock()

    mock_locator.auth_service.get_user_from_token.return_value = User(
        id=1,
        username="test_user",
        email="test@example.com",
        password_hash="hash",
        full_name="Test User",
        role="manager",
        is_active=True,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )

    with patch("core.service_locator._locator", mock_locator):
        from main import app
        client = TestClient(app)
        client.headers.update({"Authorization": "Bearer testtoken"})
        yield client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_list_projects(client):
    response = client.get("/api/projects/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert len(data["items"]) == 1
    assert data["items"][0]["code"] == "PRJ-001"
    assert data["items"][0]["status"] == "active"


def test_tender_assessment_go(client):
    response = client.post(
        "/api/tender/assess",
        json={
            "tender_name": "TENDER-001",
            "customer": "Test Customer",
            "deadline_date": "2026-12-31",
            "documents": [
                {"doc_type": "Technical", "count": 10, "hours_per_doc": 8},
                {"doc_type": "Assembly", "count": 5, "hours_per_doc": 12},
            ],
            "team_size": 5,
            "vdr_required": False,
            "otk_required": False,
            "logistics_complexity": "normal",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assessment"]["decision"] == "GO"
    assert data["team_capacity"]["total_engineers"] == 5
    assert data["requirements"]["total_hours"] == 140.0


def test_create_project_from_tender(client):
    response = client.post(
        "/api/projects/create-from-tender",
        json={
            "tender_name": "Test Tender",
            "customer": "Test Customer",
            "deadline_date": "2026-12-31",
            "documents": [
                {"doc_type": "Technical", "count": 5, "hours_per_doc": 10, "discipline": "Engineering"},
            ],
            "team_size": 3,
            "vdr_required": True,
            "otk_required": True,
            "logistics_complexity": "normal",
            "custom_fields": {"customer_specific": "value"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert data["project"]["name"] == "Test Tender"
    assert data["tasks_created"] > 0
    assert "message" in data
