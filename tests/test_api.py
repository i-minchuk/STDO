"""Tests for API endpoints using FastAPI TestClient."""

from unittest.mock import MagicMock, patch
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from models.project import Project
from models.enums import ProjectStatus


@pytest.fixture
def client():
    """Create a test client with mocked service locator."""
    mock_locator = MagicMock()

    # Mock project_repo.list_all
    mock_locator.project_repo.list_all.return_value = [
        Project(
            id=1, code="PRJ-001", name="Test Project",
            customer="Test", status=ProjectStatus.ACTIVE,
            manager_id=1, start_date=date(2026, 1, 1),
            end_date_planned=date(2026, 12, 31),
            end_date_forecast=None, end_date_actual=None,
            created_at=datetime(2026, 1, 1),
        )
    ]

    with patch("core.service_locator._locator", mock_locator):
        from main import app
        yield TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_projects(client):
    response = client.get("/api/projects/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "PRJ-001"
    assert data[0]["status"] == "active"
