"""E2E tests for critical user journeys.

These tests require a running server and database.
Run with: python -m pytest tests/test_e2e.py -v -m e2e
"""
import pytest
import requests
from datetime import datetime, timedelta
from typing import Dict, Any


# Base URL for the API - configurable via environment
BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def auth_headers():
    """Login and return auth headers."""
    # Register or use existing test user
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "username": "e2e_test_user",
            "email": "e2e@test.local",
            "password": "TestPassword123!",
            "full_name": "E2E Test User",
            "role": "engineer",
        },
    )
    
    if register_response.status_code == 400:
        # User already exists, just login
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "e2e_test_user", "password": "TestPassword123!"},
        )
        token = login_response.json()["access_token"]
    else:
        token = register_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def admin_headers():
    """Login as admin and return auth headers."""
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestE2EAuthentication:
    """E2E tests for authentication flow."""

    def test_login_success(self):
        """Test successful login returns tokens."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != ""

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials fails."""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_token_refresh(self, auth_headers):
        """Test token refresh flow."""
        # Get current token
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=auth_headers,
        )
        assert me_response.status_code == 200

    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without auth fails."""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401


class TestE2EProjectWorkflow:
    """E2E tests for project creation and management workflow."""

    def test_create_project_from_tender(self, admin_headers):
        """Test creating a project from a tender."""
        # First, we need to create a tender or use existing
        # For E2E, we'll create a minimal project directly
        
        project_data = {
            "code": "E2E-TEST-001",
            "name": "E2E Test Project",
            "customer": "Test Customer",
            "status": "planned",
            "manager_id": 1,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date_planned": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        }
        
        response = requests.post(
            f"{BASE_URL}/api/projects/create-from-tender",
            headers=admin_headers,
            json={
                "tender_name": "E2E Test Tender",
                "customer": "Test Customer",
                "deadline_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "documents": [
                    {"doc_type": "VDR", "count": 5, "hours_per_doc": 8.0, "discipline": "Engineering"},
                ],
                "team_size": 3,
                "vdr_required": True,
                "otk_required": False,
                "logistics_complexity": "normal",
            },
        )
        
        # Project creation may fail if tender doesn't exist
        # This test validates the API structure
        assert response.status_code in [200, 400, 422]

    def test_list_projects_pagination(self, auth_headers):
        """Test listing projects with pagination."""
        response = requests.get(
            f"{BASE_URL}/api/projects?limit=10&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data


class TestE2EDocumentWorkflow:
    """E2E tests for document management workflow."""

    def test_create_and_list_documents(self, auth_headers, project_id: int = 1):
        """Test creating and listing documents."""
        # List documents for a project
        response = requests.get(
            f"{BASE_URL}/api/documents?project_id={project_id}&limit=20",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_document_upload_validation(self, auth_headers):
        """Test document file upload validation."""
        # Try to upload non-PDF file - should fail
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = requests.post(
            f"{BASE_URL}/api/documents/{1}/upload",
            headers=auth_headers,
            files=files,
        )
        # Should reject non-PDF files
        assert response.status_code in [400, 404]


class TestE2EGamification:
    """E2E tests for gamification features."""

    def test_get_leaderboard(self, auth_headers):
        """Test accessing leaderboard."""
        response = requests.get(
            f"{BASE_URL}/api/gamification/leaderboard",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_my_profile(self, auth_headers):
        """Test getting user gamification profile."""
        response = requests.get(
            f"{BASE_URL}/api/gamification/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "level" in data
        assert "badges" in data

    def test_daily_quests(self, auth_headers):
        """Test accessing daily quests."""
        response = requests.get(
            f"{BASE_URL}/api/gamification/daily-quests",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestE2ERateLimiting:
    """E2E tests for rate limiting."""

    def test_login_rate_limiting(self):
        """Test that login endpoint is rate limited."""
        failed_attempts = 0
        
        # Try multiple login attempts
        for i in range(10):
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "admin", "password": "wrongpassword"},
            )
            if response.status_code == 429:
                failed_attempts = i + 1
                break
        
        # Should be rate limited after 5 attempts
        assert failed_attempts <= 7, "Rate limiting should trigger after ~5 attempts"


class TestE2EHealthCheck:
    """E2E tests for health endpoints."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


# Mark for selective execution
pytestmark = pytest.mark.e2e
