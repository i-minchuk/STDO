"""Tests for UserRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone


class TestUserRepository:
    """Tests for UserRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create UserRepository with mocked database."""
        from repositories.user_repository import UserRepository
        return UserRepository(db=mock_db)

    def test_get_by_id(self, repo, mock_db):
        """Test retrieving a user by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "username": "testuser", "email": "test@example.com",
            "password_hash": "hashed", "full_name": "Test User",
            "role": "engineer", "is_active": True,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
        }

        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.username == "testuser"

    def test_get_by_id_not_found(self, repo, mock_db):
        """Test retrieving a non-existent user."""
        mock_db.fetch_one.return_value = None

        result = repo.get_by_id(999)

        assert result is None

    def test_get_by_username(self, repo, mock_db):
        """Test retrieving user by username."""
        mock_db.fetch_one.return_value = {
            "id": 1, "username": "testuser", "email": "test@example.com",
            "password_hash": "hashed", "full_name": "Test User",
            "role": "engineer", "is_active": True,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
        }

        result = repo.get_by_username("testuser")

        assert result is not None
        assert result.username == "testuser"

    def test_get_by_email(self, repo, mock_db):
        """Test retrieving user by email."""
        mock_db.fetch_one.return_value = {
            "id": 1, "username": "testuser", "email": "test@example.com",
            "password_hash": "hashed", "full_name": "Test User",
            "role": "engineer", "is_active": True,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
        }

        result = repo.get_by_email("test@example.com")

        assert result is not None
        assert result.email == "test@example.com"

    def test_get_all(self, repo, mock_db):
        """Test getting all users."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "username": "user1", "email": "user1@example.com",
                "password_hash": "hashed", "full_name": "User 1",
                "role": "engineer", "is_active": True,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
            }
        ]

        result = repo.get_all()

        assert len(result) == 1

    def test_get_all_active_only(self, repo, mock_db):
        """Test getting only active users."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "username": "user1", "email": "user1@example.com",
                "password_hash": "hashed", "full_name": "User 1",
                "role": "engineer", "is_active": True,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
            }
        ]

        result = repo.get_all(active_only=True)

        assert len(result) == 1

    def test_get_all_paginated(self, repo, mock_db):
        """Test getting users with pagination."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "username": "user1", "email": "user1@example.com",
                "password_hash": "hashed", "full_name": "User 1",
                "role": "engineer", "is_active": True,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
            }
        ]
        mock_db.fetch_one.return_value = {"cnt": 1}

        result, total = repo.get_all_paginated(limit=10, offset=0)

        assert len(result) == 1
        assert total == 1

    def test_create(self, repo, mock_db):
        """Test creating a new user."""
        mock_db.fetch_one.return_value = {
            "id": 2, "username": "newuser", "email": "new@example.com",
            "password_hash": "hashed", "full_name": "New User",
            "role": "engineer", "is_active": True,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
        }

        result = repo.create("newuser", "new@example.com", "hashed", "New User", "engineer")

        assert result is not None
        assert result.username == "newuser"

    def test_update(self, repo, mock_db):
        """Test updating a user."""
        mock_db.fetch_one.return_value = {
            "id": 1, "username": "updateduser", "email": "updated@example.com",
            "password_hash": "hashed", "full_name": "Updated User",
            "role": "manager", "is_active": True,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 1, 15, tzinfo=timezone.utc)
        }

        result = repo.update(1, username="updateduser", role="manager")

        assert result is not None
        assert result.username == "updateduser"

    def test_deactivate(self, repo, mock_db):
        """Test deactivating a user."""
        mock_db.execute.return_value = 1

        result = repo.deactivate(1)

        assert result is True
        mock_db.execute.assert_called_once()

    def test_count(self, repo, mock_db):
        """Test counting users."""
        mock_db.fetch_one.return_value = {"cnt": 10}

        result = repo.count()

        assert result == 10
