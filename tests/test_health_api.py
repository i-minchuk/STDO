"""Tests for health check endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthAPI:
    """Tests for health check endpoints."""

    def test_health_basic(self):
        """Test basic health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "DokPotok IRIS"

    def test_health_db(self):
        """Test database health endpoint."""
        response = client.get("/api/health/db")
        assert response.status_code in [200, 503]  # 200 if DB up, 503 if down
        data = response.json()
        assert "status" in data
        assert "database" in data

    def test_health_cache(self):
        """Test cache health endpoint."""
        response = client.get("/api/health/cache")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "cache_type" in data
        assert "connected" in data

    def test_health_metrics(self):
        """Test application metrics endpoint."""
        response = client.get("/api/health/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "application" in data
        assert "python" in data
        assert "process" in data

    def test_health_ready(self):
        """Test readiness probe endpoint."""
        response = client.get("/api/health/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "timestamp" in data

    def test_health_metrics_endpoint(self):
        """Test application metrics endpoint."""
        response = client.get("/api/health/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "application" in data
        assert "python" in data
        assert "process" in data

    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "DokPotok IRIS"
        assert "version" in data
        assert data["docs"] == "/docs"
