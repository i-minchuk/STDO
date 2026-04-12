"""Locust performance tests for DokPotok IRIS API."""
from locust import HttpUser, task, between, events
import json
import random


class APIUser(HttpUser):
    """Simulates a regular API user."""
    
    wait_time = between(1, 3)
    
    # Test credentials (should exist in test environment)
    username = "admin"
    password = "admin123"
    
    def on_start(self):
        """Login when user starts."""
        self.login()
    
    def login(self):
        """Authenticate and store token."""
        response = self.client.post(
            "/api/auth/login",
            json={"username": self.username, "password": self.password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Login failed: {response.status_code}")
            self.token = None
    
    @task(3)
    def get_health(self):
        """Check health endpoint."""
        self.client.get("/health")
    
    @task(5)
    def list_projects(self):
        """List projects with pagination."""
        self.client.get("/api/projects?limit=20&offset=0")
    
    @task(5)
    def list_documents(self):
        """List documents."""
        self.client.get("/api/documents?limit=20&offset=0")
    
    @task(3)
    def get_portfolio(self):
        """Get portfolio overview."""
        self.client.get("/api/projects/portfolio/today")
    
    @task(2)
    def get_leaderboard(self):
        """Get gamification leaderboard."""
        self.client.get("/api/gamification/leaderboard")
    
    @task(2)
    def get_my_profile(self):
        """Get user gamification profile."""
        self.client.get("/api/gamification/me")
    
    @task(1)
    def list_tasks(self):
        """List tasks for project."""
        self.client.get("/api/tasks?project_id=1&limit=20")
    
    @task(1)
    def get_notifications(self):
        """Get user notifications."""
        self.client.get("/api/gamification/notifications")


class ReadHeavyUser(HttpUser):
    """Simulates a read-heavy user (viewer)."""
    
    wait_time = between(2, 5)
    username = "admin"
    password = "admin123"
    
    def on_start(self):
        self.login()
    
    def login(self):
        response = self.client.post(
            "/api/auth/login",
            json={"username": self.username, "password": self.password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(10)
    def list_projects(self):
        self.client.get("/api/projects?limit=50&offset=0")
    
    @task(8)
    def list_documents(self):
        self.client.get("/api/documents?limit=50&offset=0")
    
    @task(5)
    def search_documents(self):
        self.client.get("/api/documents?search=SPEC&limit=20")
    
    @task(3)
    def get_dashboard(self):
        self.client.get("/api/projects/portfolio/today")


class WriteHeavyUser(HttpUser):
    """Simulates a write-heavy user (project manager)."""
    
    wait_time = between(3, 6)
    username = "admin"
    password = "admin123"
    
    def on_start(self):
        self.login()
    
    def login(self):
        response = self.client.post(
            "/api/auth/login",
            json={"username": self.username, "password": self.password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(2)
    def create_project_from_tender(self):
        """Create a project from tender."""
        tender_data = {
            "tender_name": f"Test Project {random.randint(1000, 9999)}",
            "customer": "Test Customer",
            "deadline_date": "2026-12-31",
            "documents": [
                {"doc_type": "VDR", "count": 5, "hours_per_doc": 8.0, "discipline": "Engineering"}
            ],
            "team_size": 3,
            "vdr_required": True,
            "otk_required": False,
            "logistics_complexity": "normal"
        }
        self.client.post("/api/projects/create-from-tender", json=tender_data)
    
    @task(3)
    def update_document_status(self):
        """Update document status (mock)."""
        # In real scenario, would use actual document ID
        self.client.put("/api/documents/1/status", json={"status": "on_review"})
    
    @task(1)
    def create_remark(self):
        """Create a remark."""
        remark_data = {
            "project_id": 1,
            "text": f"Test remark {random.randint(1000, 9999)}",
            "source": "internal"
        }
        self.client.post("/api/remarks", json=remark_data)


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test configuration when test starts."""
    print("=" * 80)
    print("Performance Test Started")
    print(f"Target URL: {environment.host}")
    print(f"Users: {environment.parsed_options.num_users}")
    print(f"Spawn Rate: {environment.parsed_options.spawn_rate}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test summary when test stops."""
    print("=" * 80)
    print("Performance Test Completed")
    print("Check Locust UI for detailed metrics")
    print("=" * 80)
