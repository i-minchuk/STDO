#!/usr/bin/env python
"""E2E Smoke Test: Document Workflow Happy Path.

Tests the complete flow:
1. Create project
2. Create document
3. Create revision
4. Approve revision

Usage:
    python tests/test_e2e_smoke.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime

from db.database import Database
from core.service_locator import get_locator, init_locator
from config import Config


async def test_e2e_document_workflow():
    """Test complete document workflow E2E."""
    print("=" * 60)
    print("E2E Smoke Test: Document Workflow")
    print("=" * 60)
    
    # Initialize
    print("\n[1/6] Initializing...")
    cfg = Config()
    init_locator(cfg)
    locator = get_locator()
    db = Database(
        dsn=cfg.db_dsn,
        min_size=2,
        max_size=5
    )
    db.connect()
    
    print(f"  Database: {cfg.db_dsn}")
    
    # Step 1: Create Project
    print("\n[2/6] Creating project...")
    project = locator.project_repo.create(
        code="TEST-001",
        name="Test Project E2E",
        customer="Test Customer",
        status="active",
        manager_id=1,  # Assuming admin user exists
        start_date=datetime.now().date(),
        end_date_planned=datetime.now().date().replace(month=datetime.now().month + 3),
    )
    print(f"  Created project: {project.code} - {project.name}")
    assert project.id is not None, "Project ID should be set"
    assert project.code == "TEST-001", "Project code mismatch"
    
    # Step 2: Create Document
    print("\n[3/6] Creating document...")
    document = locator.document_repo.create(
        project_id=project.id,
        code="АБВГ.12345.001",
        title="Test Document",
        discipline="И",
        created_by=1,
    )
    print(f"  Created document: {document.code} - {document.title}")
    assert document.id is not None, "Document ID should be set"
    assert document.project_id == project.id, "Document project_id mismatch"
    
    # Step 3: Create Revision (simplified - without file upload)
    print("\n[4/6] Creating revision...")
    revision = locator.revision_repo.create(
        document_id=document.id,
        revision_index="01",
        revision_letter="А",
        revision_number=1,
        version_number=1,
        status="in_work",
        file_path="/tmp/test_revision.pdf",
        created_by=1,
    )
    print(f"  Created revision: {revision.revision_letter}{revision.revision_number}")
    assert revision.id is not None, "Revision ID should be set"
    assert revision.status == "in_work", "Revision status should be in_work"
    
    # Step 4: Approve Revision
    print("\n[5/6] Approving revision...")
    approved_revision = locator.revision_repo.approve(
        revision_id=revision.id,
        approved_by=1,
    )
    print(f"  Approved revision: {approved_revision.status}")
    assert approved_revision.status == "approved", "Revision should be approved"
    
    # Step 5: Update document current_revision_id
    print("\n[6/6] Updating document...")
    updated_doc = locator.document_repo.update(
        document_id=document.id,
        current_revision_id=approved_revision.id,
    )
    print(f"  Document current_revision: {updated_doc.current_revision_id}")
    assert updated_doc.current_revision_id == approved_revision.id, "Document should reference approved revision"
    
    # Cleanup
    print("\n[CLEANUP] Cleaning up test data...")
    # Note: In real tests, use transactions or cleanup fixtures
    # For smoke test, we leave data for inspection
    
    print("\n" + "=" * 60)
    print("E2E SMOKE TEST PASSED")
    print("=" * 60)
    
    return True


def main():
    """Run E2E smoke test."""
    try:
        result = asyncio.run(test_e2e_document_workflow())
        return 0 if result else 1
    except Exception as e:
        print(f"\n[ERROR] E2E test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
