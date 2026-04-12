"""Tests for AuthService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from models.user import User


class TestAuthService:
    """Tests for AuthService business logic."""

    @pytest.fixture
    def mock_user_repo(self):
        """Create a mock user repository."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_user_repo):
        """Create AuthService with mocked dependencies."""
        from services.auth_service import AuthService
        return AuthService(user_repo=mock_user_repo, secret_key="test-secret")

    def test_hash_password(self, service):
        """Test password hashing."""
        hashed = service.hash_password("mypassword")

        assert hashed is not None
        assert hashed != "mypassword"

    def test_verify_password_correct(self, service):
        """Test verifying correct password."""
        hashed = service.hash_password("mypassword")

        assert service.verify_password("mypassword", hashed) is True

    def test_verify_password_incorrect(self, service):
        """Test verifying incorrect password."""
        hashed = service.hash_password("mypassword")

        assert service.verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self, service):
        """Test creating access token."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )

        token = service.create_access_token(user, expires_minutes=30)

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token(self, service):
        """Test creating refresh token."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )

        token = service.create_refresh_token(user, expires_days=7)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_token_valid(self, service):
        """Test decoding valid token."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        token = service.create_access_token(user)

        payload = service.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["type"] == "access"

    def test_decode_token_invalid(self, service):
        """Test decoding invalid token."""
        payload = service.decode_token("invalid.token.here")

        assert payload is None

    def test_authenticate_success(self, service, mock_user_repo):
        """Test successful authentication."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash=service.hash_password("mypassword"),
            full_name="Test User", role="engineer",
            is_active=True, created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        mock_user_repo.get_by_username.return_value = user

        result = service.authenticate("testuser", "mypassword")

        assert result == user

    def test_authenticate_wrong_password(self, service, mock_user_repo):
        """Test authentication with wrong password."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash=service.hash_password("mypassword"),
            full_name="Test User", role="engineer",
            is_active=True, created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        mock_user_repo.get_by_username.return_value = user

        result = service.authenticate("testuser", "wrongpassword")

        assert result is None

    def test_authenticate_inactive_user(self, service, mock_user_repo):
        """Test authentication with inactive user."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash=service.hash_password("mypassword"),
            full_name="Test User", role="engineer",
            is_active=False, created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        mock_user_repo.get_by_username.return_value = user

        result = service.authenticate("testuser", "mypassword")

        assert result is None

    def test_authenticate_user_not_found(self, service, mock_user_repo):
        """Test authentication with non-existent user."""
        mock_user_repo.get_by_username.return_value = None

        result = service.authenticate("nonexistent", "password")

        assert result is None

    def test_get_user_from_token_valid(self, service, mock_user_repo):
        """Test getting user from valid access token."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        mock_user_repo.get_by_id.return_value = user
        token = service.create_access_token(user)

        result = service.get_user_from_token(token)

        assert result == user

    def test_get_user_from_token_invalid_type(self, service, mock_user_repo):
        """Test getting user from refresh token (should fail)."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        token = service.create_refresh_token(user)

        result = service.get_user_from_token(token)

        assert result is None

    def test_refresh_access_token_success(self, service, mock_user_repo):
        """Test refreshing access token."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        mock_user_repo.get_by_id.return_value = user
        refresh_token = service.create_refresh_token(user)

        result = service.refresh_access_token(refresh_token)

        assert result is not None
        assert isinstance(result, str)

    def test_refresh_access_token_invalid_type(self, service):
        """Test refreshing with access token (should fail)."""
        user = User(
            id=1, username="testuser", email="test@example.com",
            password_hash="hash", full_name="Test User",
            role="engineer", is_active=True,
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1)
        )
        access_token = service.create_access_token(user)

        result = service.refresh_access_token(access_token)

        assert result is None

    def test_register_success(self, service, mock_user_repo):
        """Test successful user registration."""
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = MagicMock(
            id=1, username="newuser", email="new@example.com",
            role="engineer", is_active=True
        )

        result = service.register("newuser", "new@example.com", "password123", "New User")

        assert result is not None
        mock_user_repo.create.assert_called_once()

    def test_register_username_exists(self, service, mock_user_repo):
        """Test registration with existing username."""
        mock_user_repo.get_by_username.return_value = MagicMock()

        with pytest.raises(ValueError, match="already exists"):
            service.register("existinguser", "new@example.com", "password123", "New User")

    def test_register_email_exists(self, service, mock_user_repo):
        """Test registration with existing email."""
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = MagicMock()

        with pytest.raises(ValueError, match="already exists"):
            service.register("newuser", "existing@example.com", "password123", "New User")
