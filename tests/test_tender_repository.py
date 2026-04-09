"""Tests for TenderRepository."""
import pytest
from datetime import date, timedelta

from models.enums import TaskStatus, TaskType


class TestTenderRepository:
    """Test TenderRepository CRUD operations."""

    def test_insert_tender(self, test_locator, test_user, cleanup_test_db):
        """Test creating a new tender."""
        tender = test_locator.tender_repo.insert(
            name="Test Tender",
            customer="Test Customer",
            deadline_date=date.today() + timedelta(days=30),
            vdr_required=True,
            otk_required=False,
            logistics_complexity="normal",
            notes="Test notes",
            required_disciplines=["Engineering", "Design"],
            team_size=5,
            expected_review_rounds=2,
            expected_remark_count=10,
            created_by=test_user.id,
        )

        assert tender is not None
        assert tender.id is not None
        assert tender.name == "Test Tender"
        assert tender.customer == "Test Customer"
        assert tender.status == "draft"
        assert tender.vdr_required is True
        assert tender.team_size == 5

    def test_insert_tender_without_optional_fields(self, test_locator, test_user, cleanup_test_db):
        """Test creating tender with minimal fields."""
        tender = test_locator.tender_repo.insert(
            name="Minimal Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=14),
            created_by=test_user.id,
        )

        assert tender is not None
        assert tender.name == "Minimal Tender"
        assert tender.status == "draft"
        assert tender.required_disciplines is None

    def test_get_by_id(self, test_locator, test_user, test_tender, cleanup_test_db):
        """Test getting tender by ID."""
        retrieved = test_locator.tender_repo.get_by_id(test_tender.id)

        assert retrieved is not None
        assert retrieved.id == test_tender.id
        assert retrieved.name == test_tender.name

    def test_get_by_id_nonexistent(self, test_locator, cleanup_test_db):
        """Test getting non-existent tender returns None."""
        result = test_locator.tender_repo.get_by_id(99999)

        assert result is None

    def test_get_all_with_pagination(self, test_locator, test_user, cleanup_test_db):
        """Test get_all returns paginated results."""
        # Create multiple tenders
        for i in range(5):
            test_locator.tender_repo.insert(
                name=f"Tender {i}",
                customer="Customer",
                deadline_date=date.today() + timedelta(days=30),
                created_by=test_user.id,
            )

        tenders = test_locator.tender_repo.get_all(limit=2, offset=0)

        assert len(tenders) == 2

    def test_get_by_status(self, test_locator, test_user, test_tender, cleanup_test_db):
        """Test filtering by status."""
        # Create another tender with different status
        test_locator.tender_repo.insert(
            name="Another Tender",
            customer="Customer",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        # Update status of first tender
        test_locator.tender_repo.update_status(test_tender.id, "assessed")

        draft_tenders = test_locator.tender_repo.get_by_status("draft", limit=10, offset=0)
        assessed_tenders = test_locator.tender_repo.get_by_status("assessed", limit=10, offset=0)

        assert len(draft_tenders) == 1
        assert len(assessed_tenders) == 1
        assert assessed_tenders[0].status == "assessed"

    def test_update_status(self, test_locator, test_user, test_tender, cleanup_test_db):
        """Test updating tender status."""
        assessment = {"decision": "GO", "feasibility_pct": 85}
        
        updated = test_locator.tender_repo.update_status(
            test_tender.id, "assessed", assessment
        )

        assert updated.status == "assessed"
        assert updated.assessment_result is not None
        assert updated.assessment_result["decision"] == "GO"

    def test_update_status_preserves_assessment(self, test_locator, test_user, test_tender, cleanup_test_db):
        """Test that updating status preserves assessment_result."""
        assessment = {"decision": "GO", "feasibility_pct": 90}
        test_locator.tender_repo.update_status(test_tender.id, "assessed", assessment)

        # Update to approved
        updated = test_locator.tender_repo.update_status(
            test_tender.id, "approved", {"decision": "GO", "feasibility_pct": 90}
        )

        assert updated.status == "approved"
        assert updated.assessment_result is not None

    def test_delete_tender(self, test_locator, test_user, test_tender, cleanup_test_db):
        """Test deleting a tender."""
        tender_id = test_tender.id
        success = test_locator.tender_repo.delete(tender_id)

        assert success is True
        assert test_locator.tender_repo.get_by_id(tender_id) is None

    def test_delete_nonexistent_tender(self, test_locator, cleanup_test_db):
        """Test deleting non-existent tender returns False."""
        result = test_locator.tender_repo.delete(99999)

        assert result is False

    def test_add_document(self, test_locator, test_user, test_tender, cleanup_test_db):
        """Test adding document to tender."""
        doc = test_locator.tender_repo.add_document(
            tender_id=test_tender.id,
            doc_type="Specification",
            count=10,
            hours_per_doc=8.0,
            discipline="Engineering",
        )

        assert doc is not None
        assert doc.doc_type == "Specification"
        assert doc.count == 10
        assert doc.hours_per_doc == 8.0

    def test_get_documents(self, test_locator, test_user, test_tender_with_docs, cleanup_test_db):
        """Test getting documents for tender."""
        docs = test_locator.tender_repo.get_documents(test_tender_with_docs.id)

        assert len(docs) == 2
        doc_types = [d.doc_type for d in docs]
        assert "Specification" in doc_types
        assert "Drawing" in doc_types

    def test_get_filtered_by_status(self, test_locator, test_user, cleanup_test_db):
        """Test get_filtered with status filter."""
        # Create tenders with different statuses
        t1 = test_locator.tender_repo.insert(
            name="Tender 1", customer="C1",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        t2 = test_locator.tender_repo.insert(
            name="Tender 2", customer="C2",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        test_locator.tender_repo.update_status(t1.id, "assessed")

        tenders, total = test_locator.tender_repo.get_filtered(status="assessed")

        assert total == 1
        assert tenders[0].status == "assessed"

    def test_get_filtered_by_customer(self, test_locator, test_user, cleanup_test_db):
        """Test get_filtered with customer filter."""
        test_locator.tender_repo.insert(
            name="Tender A", customer="Acme Corp",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )
        test_locator.tender_repo.insert(
            name="Tender B", customer="Beta Inc",
            deadline_date=date.today() + timedelta(days=30),
            created_by=test_user.id,
        )

        tenders, total = test_locator.tender_repo.get_filtered(customer="Acme")

        assert total == 1
        assert "Acme" in tenders[0].customer

    def test_get_filtered_pagination(self, test_locator, test_user, cleanup_test_db):
        """Test get_filtered pagination returns correct total."""
        for i in range(10):
            test_locator.tender_repo.insert(
                name=f"Tender {i}", customer="Customer",
                deadline_date=date.today() + timedelta(days=30),
                created_by=test_user.id,
            )

        tenders, total = test_locator.tender_repo.get_filtered(limit=3, offset=0)

        assert total == 10
        assert len(tenders) == 3

    def test_row_to_model_none(self):
        """Test _row_to_model handles None input."""
        from repositories.tender_repository import TenderRepository
        
        result = TenderRepository._row_to_model(None)
        assert result is None
