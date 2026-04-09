"""Tests for Tender API endpoints."""
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient


class TestTenderAPI:
    """Test Tender API endpoints."""

    def test_assess_tender_requires_auth(self, test_locator):
        """Test that assess endpoint requires authentication."""
        from main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/tender/assess",
            json={
                "tender_name": "Test",
                "customer": "Customer",
                "deadline_date": (date.today() + timedelta(days=30)).isoformat(),
                "documents": [{"doc_type": "Spec", "count": 10, "hours_per_doc": 8.0}],
            },
        )
        
        # Should return 401 or 403 without auth
        assert response.status_code in (401, 403)

    def test_assess_tender_validation_empty_documents(self, test_locator, test_user):
        """Test validation rejects empty documents list."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        # Create token for test user
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.post(
            "/api/tender/assess",
            json={
                "tender_name": "Test",
                "customer": "Customer",
                "deadline_date": (date.today() + timedelta(days=30)).isoformat(),
                "documents": [],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 422  # Validation error

    def test_assess_tender_validation_past_deadline(self, test_locator, test_user):
        """Test validation rejects past deadline."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.post(
            "/api/tender/assess",
            json={
                "tender_name": "Test",
                "customer": "Customer",
                "deadline_date": (date.today() - timedelta(days=1)).isoformat(),
                "documents": [{"doc_type": "Spec", "count": 10, "hours_per_doc": 8.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 422  # Validation error

    def test_assess_tender_validation_invalid_count(self, test_locator, test_user):
        """Test validation rejects zero/negative document count."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.post(
            "/api/tender/assess",
            json={
                "tender_name": "Test",
                "customer": "Customer",
                "deadline_date": (date.today() + timedelta(days=30)).isoformat(),
                "documents": [{"doc_type": "Spec", "count": 0, "hours_per_doc": 8.0}],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 422

    def test_list_tenders_requires_auth(self, test_locator):
        """Test that list endpoint requires authentication."""
        from main import app
        
        client = TestClient(app)
        response = client.get("/api/tender/")
        
        assert response.status_code in (401, 403)

    def test_list_tenders_returns_pagination(self, test_locator, test_user):
        """Test list tenders returns total/limit/offset."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        # Create a tender
        test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.get(
            "/api/tender/",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tenders" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    def test_get_tender_requires_auth(self, test_locator):
        """Test that get tender endpoint requires authentication."""
        from main import app
        
        client = TestClient(app)
        response = client.get("/api/tender/1")
        
        assert response.status_code in (401, 403)

    def test_get_tender_not_found(self, test_locator, test_user):
        """Test 404 for non-existent tender."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.get(
            "/api/tender/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404

    def test_delete_tender_requires_admin_role(self, test_locator, test_user):
        """Test that delete requires admin/manager role."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        # Create tender
        tender = test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        
        # Engineer role should be denied
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.delete(
            f"/api/tender/{tender.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    def test_delete_tender_with_admin_role(self, test_locator, test_admin_user):
        """Test delete succeeds with admin role."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        # Create tender
        tender = test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_admin_user.id,
        )
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_admin_user.username, "user_id": test_admin_user.id}
        )
        
        client = TestClient(app)
        response = client.delete(
            f"/api/tender/{tender.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200

    def test_update_status_requires_admin_role(self, test_locator, test_user):
        """Test that status update requires admin/manager role."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        tender = test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_user.username, "user_id": test_user.id}
        )
        
        client = TestClient(app)
        response = client.post(
            f"/api/tender/{tender.id}/status",
            params={"status": "approved"},
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    def test_update_status_with_manager_role(self, test_locator, test_manager_user):
        """Test status update succeeds with manager role."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        tender = test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_manager_user.id,
        )
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_manager_user.username, "user_id": test_manager_user.id}
        )
        
        client = TestClient(app)
        response = client.post(
            f"/api/tender/{tender.id}/status",
            params={"status": "approved"},
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    def test_update_status_invalid_status(self, test_locator, test_manager_user):
        """Test invalid status is rejected."""
        from main import app
        from core.service_locator import init_locator
        
        init_locator(test_locator._config)
        
        tender = test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_manager_user.id,
        )
        
        token = test_locator.auth_service.create_access_token(
            {"sub": test_manager_user.username, "user_id": test_manager_user.id}
        )
        
        client = TestClient(app)
        response = client.post(
            f"/api/tender/{tender.id}/status",
            params={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 400
