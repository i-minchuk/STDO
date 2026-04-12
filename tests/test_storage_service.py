"""Tests for StorageService."""
import pytest
import os
import tempfile
from unittest.mock import MagicMock
from io import BytesIO


class TestStorageService:
    """Tests for StorageService business logic."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def service(self, temp_dir):
        """Create StorageService with temp directory."""
        from services.storage_service import StorageService
        return StorageService(storage_root=temp_dir)

    def test_save_revision_file_creates_directories(self, service, temp_dir):
        """Test that save_revision_file creates necessary directories."""
        file_content = BytesIO(b"test content")

        result = service.save_revision_file(
            project_code="PRJ-001",
            document_code="DOC-001",
            version_number=1,
            filename="test.pdf",
            content=file_content,
        )

        expected_dir = os.path.join(temp_dir, "PRJ-001", "DOC-001")
        assert os.path.isdir(expected_dir)
        assert "v0001_test.pdf" in result

    def test_save_revision_file_stores_content(self, service, temp_dir):
        """Test that file content is stored correctly."""
        test_content = b"Hello, World!"
        file_content = BytesIO(test_content)

        result = service.save_revision_file(
            project_code="PRJ-001",
            document_code="DOC-001",
            version_number=1,
            filename="test.pdf",
            content=file_content,
        )

        assert os.path.isfile(result)
        with open(result, "rb") as f:
            assert f.read() == test_content

    def test_save_revision_file_multiple_versions(self, service, temp_dir):
        """Test saving multiple versions of the same document."""
        file_content1 = BytesIO(b"version 1")
        file_content2 = BytesIO(b"version 2")

        path1 = service.save_revision_file(
            project_code="PRJ-001",
            document_code="DOC-001",
            version_number=1,
            filename="test.pdf",
            content=file_content1,
        )

        path2 = service.save_revision_file(
            project_code="PRJ-001",
            document_code="DOC-001",
            version_number=2,
            filename="test.pdf",
            content=file_content2,
        )

        assert "v0001_test.pdf" in path1
        assert "v0002_test.pdf" in path2
        assert os.path.isfile(path1)
        assert os.path.isfile(path2)

    def test_save_revision_file_sanitizes_project_code(self, service, temp_dir):
        """Test that project code is sanitized."""
        file_content = BytesIO(b"test")

        result = service.save_revision_file(
            project_code="PRJ/001\\bad",
            document_code="DOC-001",
            version_number=1,
            filename="test.pdf",
            content=file_content,
        )

        # Bad characters should be replaced with underscores
        assert "PRJ_001_bad" in result or "PRJ_001" in result

    def test_save_revision_file_sanitizes_document_code(self, service, temp_dir):
        """Test that document code is sanitized."""
        file_content = BytesIO(b"test")

        result = service.save_revision_file(
            project_code="PRJ-001",
            document_code="DOC/001\\bad",
            version_number=1,
            filename="test.pdf",
            content=file_content,
        )

        # Bad characters should be replaced with underscores
        assert "DOC_001" in result

    def test_file_exists_true(self, service, temp_dir):
        """Test file_exists when file exists."""
        file_content = BytesIO(b"test")

        path = service.save_revision_file(
            project_code="PRJ-001",
            document_code="DOC-001",
            version_number=1,
            filename="test.pdf",
            content=file_content,
        )

        assert service.file_exists(path) is True

    def test_file_exists_false(self, service):
        """Test file_exists when file doesn't exist."""
        assert service.file_exists("/nonexistent/path/file.pdf") is False

    def test_sanitize_removes_special_chars(self, service):
        """Test that _sanitize removes special characters."""
        assert service._sanitize("test@#$%file") == "test____file"
        assert service._sanitize("normal-file") == "normal-file"
        assert service._sanitize("file_with.123") == "file_with.123"
